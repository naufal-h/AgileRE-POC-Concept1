from django.shortcuts import render, redirect
from django.views.decorators.cache import cache_page
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from .form import *
from .models import *
from plantweb.render import render as renderUml
import inflect
import spacy
from concept1.models import Project
from ucase.models import Aktor,  Ucase
from transformers import pipeline

nlp = spacy.load("model-best")

# Create your views here.
@cache_page(2)

@login_required(login_url='login')
def InputDiagram (request):
    context = {}
    
    # Memproses Input
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.save()
            
        input = form.cleaned_data['deskripsi_project']
        
        # Parse Actor dan Use Case
        nlp_sents = spacy.load("en_core_web_sm")
        p = inflect.engine()
        actors = set()
        usecase = set()
        actors_dict = {}
        current_actor = None
        input = input.lower()
        doc = nlp(input)

        for ent in doc.ents:
            if ent.label_ == "ACTOR":
                singular_actor = p.singular_noun(ent.text) or ent.text
                actors.add(singular_actor)
            elif ent.label_ == "ACTIVITY":
                usecase.add(ent.text)

        for sent in nlp_sents(input).sents:
            for ent in nlp(sent.text).ents:
                if ent.label_ == "ACTOR":
                    current_actor = p.singular_noun(ent.text) or ent.text
                elif ent.label_ == "ACTIVITY":
                    actor_key = current_actor or actors_dict.get(None)
                    if actor_key not in actors_dict:
                        actors_dict[actor_key] = set()
                    actors_dict[actor_key].add(ent.text)

        # save Aktor dan Use Case di Database
        for actor in actors_dict:
            
            aktor = Aktor(nama_aktor=actor, project=project)
            aktor.save()
            
            # Access ucase actors_dict[actor]
            for ucase in actors_dict[actor]:
                ukase = Ucase(use_case=ucase, aktor=aktor)
                ukase.save()
        
        # Kembalikan ke Home
        return redirect('home')
    
    # Tampilkan Form
    else:
        form = ProjectForm()
        context['form']= form
    
    return render(request, 'input_diagram.html', context)

@login_required(login_url='login')
def DiagramPage (request, pk):
    context = {}
    
    # Query project dan 
    project = Project.objects.get(pk=pk)
    aktors = project.aktor_set.all()
    
    content = {} 
    content["title"] = project.judul_project
    content["actors_uml"] = []
    content["ucase_uml"] = []
    content["rel_uml"] = []
    use_case = []
    i = 1

    for aktor in aktors:
        content["actors_uml"].append(f"actor {aktor.nama_aktor}")
        ucases = aktor.ucase_set.all()
        
        for ucase in ucases:
            use_case.append(ucase)
            content["ucase_uml"].append(f'usecase "{ucase.use_case}" as uc{i}')
            content["rel_uml"].append(f'{aktor.nama_aktor} --> uc{i}')
            i+=1
      
    UML =  '\n left to right direction\n {}\n\n package "{}"{{\n {}\n }}\n\n {}\n \n'.format('\n '.join(content["actors_uml"]), content['title'], '\n '.join(content["ucase_uml"]), '\n '.join(content["rel_uml"]))
    
    
    
    output = renderUml(
        UML,
        engine='plantuml',
        format='svg',
        cacheopts={
            'use_cache': False
        }
    )

    result = output[0].decode('utf-8')
    
    context['diagram'] = result
    context['title'] = content["title"]
    context['ucases'] = use_case
    
    return render(request, 'diagram.html', context)

@login_required(login_url='login')
def InputSpec (request, ucase_id):
    context = {}
    ucase = Ucase.objects.get(pk=ucase_id)
    try:
        spec = ucase.spec
    except ObjectDoesNotExist:
        spec = None
    # dd(spec)
    # ---- Kalo spec ada, tampilin
    if spec:
        return redirect('ucase:spec', pk=spec.id)
    
    # ---- Kalo spec gaada, input
    if request.method == "POST":
        form = SpecForm(request.POST)
        if form.is_valid():
            
            spec = Spec(
                ucase = ucase,
                deskripsi = form.cleaned_data['deskripsi'],
                flow = form.cleaned_data['flow']
            )
            
            # Spec
            classifier = pipeline("zero-shot-classification", model="MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli")
            threshold = 0.5
            fallback_label = 'goal'
            # paragraph_to_classify = """
            #     The administrator has the authority to manage user accounts and staff members. 
            #     This use case allows the admin to add new staff members to the system and address any account-related issues as needed.
            #     The admin logs into the system. The admin can add new staff members or update existing user accounts. If there are account-related issues, the admin can lock or unlock user accounts and reset passwords.
            # """
            paragraph_to_classify = form.cleaned_data['deskripsi']

            candidate_labels = ['goal', 'post conditions', 'preconditions']

            # Split the paragraph into sentences
            sentences = [sentence.strip() for sentence in paragraph_to_classify.split('.') if sentence]

            # Dictionary to store results for each label
            label_result = {}

            for label in candidate_labels:
                # Initialize an empty list for each label
                label_result[label] = []

            for sentence in sentences:
                # Ensure there's at least one label and one sequence
                if not candidate_labels or not sentence:
                    continue
                
                output = classifier(sentence, candidate_labels, multi_label=False)

                highest_score_index, highest_score = max(enumerate(output['scores']), key=lambda x: x[1])
                highest_score_label = output['labels'][highest_score_index]

                # Check if the highest score surpasses the threshold, otherwise assign to 'main flow'
                selected_flow = sentence if highest_score > threshold else sentence

                # Append the sentence to the corresponding label list
                label_result[highest_score_label].append(selected_flow)

            for key, value in label_result.items():
                if value:
                    label_result[key] = '. '.join(value)
                    
            if label_result['goal']:       
                spec.goal = label_result['goal']
                
            if label_result['preconditions']:       
                spec.awal = label_result['preconditions']
                
            if label_result['post conditions']:       
                spec.akhir = label_result['post conditions']
            spec.save()
            
            label_result2 = {'main flow' : ['pertama','kedua','ketiga'], 'alt flow' : ['pertama'], 'exc flow' : ['pertama','kedua','ketiga']}
            
            # Flow
            if label_result2['main flow']:
                for main in label_result2['main flow']:
                    spec.skenario_set.create(
                        step = main,
                        category = 'N'
                    )
            
            if label_result2['alt flow']:
                for alt in label_result2['alt flow']:
                    spec.skenario_set.create(
                        step = alt,
                        category = 'ALT'
                    )
            
            if label_result2['exc flow']:
                for exc in label_result2['exc flow']:
                    spec.skenario_set.create(
                        step = exc,
                        category = 'EXC'
                    )
            
            
        
        return redirect('ucase:spec', pk=spec.id)

    else:
        form = SpecForm()
        context['form']= form
        context['ucase']=ucase
    
    return render(request, 'input_spec.html', context)

@login_required(login_url='login')
def specpage (request, pk):
    context = {}
    spec = Spec.objects.get(pk=pk)
    skenarios = spec.skenario_set.all()
    flows = {
        'Normal' : [],
        'Exception' : [],
        'Alternative' : []
    }
    
    for skenario in skenarios:
        match skenario.category:
            case 'N':
                flows['Normal'].append(skenario.step)
            case 'ALT':
                flows['Alternative'].append(skenario.step)
            case 'EXC':
                flows['Exception'].append(skenario.step)
    
    context['spec'] = spec
    context['flows'] = flows
    # dd(context['flows'])
    return render(request, 'spec.html', context)