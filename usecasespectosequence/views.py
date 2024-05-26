from django.shortcuts import render, redirect
from usecasespectosequence.models import Usecase, Steps
from ucase.models import Ucase, Spec

# Create your views here.
def form_tambah_usecasespec(request, project_id, usecase_id):
    if(Usecase.objects.filter(ucase_id=usecase_id).exists()):
        task = Usecase.objects.get(ucase_id=usecase_id)
        tasks2 = Steps.objects.filter(spec_id=task.id ,is_alter=0)
        tasks3 = Steps.objects.filter(spec_id=task.id ,is_alter=1)
        context = {
            'usecase_id':usecase_id,
            'project_id':project_id,
            'usecase_name':task.usecase_name,
            'actor':task.actor,
            'desc':task.desc,
            'precon':task.precon,
            'precon_object':task.precon_object,
            'postcon':task.postcon,
            'postcon_object':task.postcon_object,
            'steps' : tasks2,
            'steps2' : tasks3,
            'range':[1,2,3,4,5,6,7,8,9,10]
        }
    else:   
        tasks = Ucase.objects.get(id=usecase_id)
        tasks1 = Spec.objects.get(ucase_id=usecase_id)
        tasks2 = Steps.objects.filter(spec_id=usecase_id ,is_alter=0)
        tasks3 = Steps.objects.filter(spec_id=usecase_id ,is_alter=1)
        context = {
            'usecase_id':usecase_id,
            'project_id':project_id,
            'usecase_name':tasks.use_case,
            'actor':tasks.aktor,
            'desc':tasks1.deskripsi,
            'postcon':tasks1.awal,
            'postcon_object':tasks1.awal,
            'precon':tasks1.akhir,
            'precon_object':tasks1.akhir,
            'steps' : tasks2,
            'steps2' : tasks3,
            'range':[1,2,3,4,5,6,7,8,9,10]
        }
        # a = tasks2[1].object
        # raise Exception()

    return render(request,'form.html',context)

def tambah_usecasespec(request,project_id,usecase_id):
    new_form = Usecase(
        project_id=project_id,
        ucase_id=usecase_id, 
        usecase_name=request.POST['usecase_name'], 
        actor=request.POST['actor'], 
        desc=request.POST['desc'],
        precon=request.POST['precon'],
        precon_object=request.POST['precon_object'], 
        postcon=request.POST['postcon'],
        postcon_object=request.POST['postcon_object'])
    
    new_form.save()  
    return redirect('/usecasespectosequence/home/'+str(project_id)+'/usecase/'+str(usecase_id)+'/form')  


def form_tambah_step(request,project_id,usecase_id):
    tasks = Steps.objects.filter(spec_id=usecase_id)  
    tasks.delete()
    ucase = Usecase.objects.get(ucase_id=usecase_id)
    for i in range(10) :
        if(bool(request.POST.get("subject_normal_"+str(i+1)) != '') and bool(request.POST.get("activity_normal_"+str(i+1)) != '') and bool(request.POST.get("activity_normal_"+str(i+1)) != '')):
            p = Steps(
                is_alter=request.POST.get("is_alter_normal_"+str(i+1)),
                subject=request.POST.get("subject_normal_"+str(i+1)),
                activity=request.POST.get("activity_normal_"+str(i+1)),
                object=request.POST.get("object_normal_"+str(i+1)),
                spec_id=ucase.id)
            p.save()
            
    for i in range(10) :
        if(bool(request.POST.get("subject_alternative_"+str(i+1)) != '') and bool(request.POST.get("activity_alternative_"+str(i+1)) != '') and bool(request.POST.get("activity_alternative_"+str(i+1)) != '')):
            p = Steps(
                is_alter=request.POST.get("is_alter_alternative_"+str(i+1)),
                subject=request.POST.get("subject_alternative_"+str(i+1)),
                activity=request.POST.get("activity_alternative_"+str(i+1)),
                object=request.POST.get("object_alternative_"+str(i+1)),
                spec_id=ucase.id)
            p.save()

    return redirect('/usecasespectosequence/home/'+str(project_id)+'/usecase/'+str(usecase_id)+'/form')  

def translasi(usecase_id):
    # Ambil object
    u = Usecase.objects.get(ucase_id=usecase_id)
    s = Steps.objects.filter(spec=u.id)

    # Variabel objek-objek untuk dimasukkan ke dalam UMLscript
    actor = '"' + u.actor + '"'
    usecase = '"' + u.usecase_name.replace(" ", "") + "Controller" + '"'
    precon_obj = '"' + u.precon_object + '"'
    postcon_obj = '"' + u.postcon_object + '"'

    # Dictionary
    objek = {
        "actor": "actor",
        "usecase": "control",
        "precon_obj": "boundary",
    }
    if "Database" in postcon_obj or "database" in postcon_obj:
        objek["postcon_obj"] = "entity"
    else:
        objek["postcon_obj"] = "boundary"

    # List langkah-langkah untuk tiap bagian
    step_subjects = list(s.values_list("subject", flat=True))
    step_activities = list(s.values_list("activity", flat=True))
    step_objects = list(s.values_list("object", flat=True))
    step_alter = list(s.values_list("is_alter", flat=True))

    # List hasil translasi dan interaksi untuk objek-objek
    hasil_translasi = ["@startuml"]
    translasi_steps = list(range(len(s)))

    # UMLscript
    hasil_translasi.append("actor " + actor)
    hasil_translasi.append("boundary " + precon_obj)
    hasil_translasi.append("control " + usecase)
    if objek["postcon_obj"] == "entity":
        hasil_translasi.append("entity " + postcon_obj)
    else:
        hasil_translasi.append("boundary " + postcon_obj)

    # Loop untuk seluruh langkah-langkah dalam satu use case
    # Aturan hubungan diagram sequence: actor->boundary, boundary->control, control->boundary atau entity, entity->control
    for i in translasi_steps:
        if step_alter[i] == False: # Skenario normal
            if step_subjects[i] == u.actor: # Jika subjek langkah adalah aktor
                if step_objects[i] == u.postcon_object and objek["postcon_obj"] == "boundary":
                    translasi_steps[i] = actor + "->" + postcon_obj + ": " + step_activities[i] # actor->boundary
                else:
                    translasi_steps[i] = actor + "->" + precon_obj + ": " + step_activities[i] # actor->boundary
            else:
                if step_subjects[i-1] == u.actor:
                    if str(u.precon_object) in translasi_steps[i-1]:
                        translasi_steps[i] = precon_obj + "->" + usecase + ": " + step_activities[i] # boundary->control
                    elif str(u.postcon_object) in translasi_steps[i-1]:
                        translasi_steps[i] = postcon_obj + "->" + usecase + ": " + step_activities[i] # boundary->control atau entity->control
                elif step_objects[i] == actor:
                    if step_objects[i-1] == u.precon_object:
                        translasi_steps[i] = precon_obj + "->" + actor + ": " + step_activities[i] # boundary->control
                    elif step_objects[i-1] == u.postcon_object and objek["postcon_obj"] == "boundary":
                        translasi_steps[i] = postcon_obj + "->" + actor + ": " + step_activities[i] # boundary->control
                else:
                    if step_objects[i] == u.precon_object: 
                        translasi_steps[i] = usecase + "->" + precon_obj + ": " + step_activities[i] # control->boundary
                    elif step_objects[i] == u.postcon_object:
                        translasi_steps[i] = usecase + "->" + postcon_obj + ": " + step_activities[i] # control->boundary atau control->entity
        elif step_alter[i] == True: # Skenario alternatif
            if step_subjects[i] == u.actor: # Jika subjek langkah adalah aktor
                if step_objects[i] == u.postcon_object and objek["postcon_obj"] == "boundary":
                    translasi_steps[i] = actor + "->" + postcon_obj + ": " + step_activities[i] # actor->boundary
                else:
                    translasi_steps[i] = actor + "->" + precon_obj + ": " + step_activities[i] # actor->boundary
            else:
                if str(u.precon_object) in step_objects[i]:
                    translasi_steps[i] = precon_obj + "->" + usecase + ": " + step_activities[i] # boundary->control
                elif str(u.postcon_object) in step_objects[i]:
                    translasi_steps[i] = postcon_obj + "->" + usecase + ": " + step_activities[i] # boundary->control atau entity->control
                elif step_objects[i] == actor:
                    if step_objects[i-1] == u.precon_object:
                        translasi_steps[i] = precon_obj + "->" + actor + ": " + step_activities[i] # boundary->control
                    elif step_objects[i-1] == u.postcon_object and objek["postcon_obj"] == "boundary":
                        translasi_steps[i] = postcon_obj + "->" + actor + ": " + step_activities[i] # boundary->control
                else:
                    if step_objects[i] == u.precon_object: 
                        translasi_steps[i] = usecase + "->" + precon_obj + ": " + step_activities[i] # control->boundary
                    elif step_objects[i] == u.postcon_object:
                        translasi_steps[i] = usecase + "->" + postcon_obj + ": " + step_activities[i] # control->boundary atau control->entity

    # Menambahkan kata end jika ada skenario alternatif
    #if True in step_alter:
    #    translasi_steps.append("alt alternative")
    #    translasi_steps.append("end")

    # Menghilangkan angka dalam list translasi_steps
    #for i in translasi_steps:
    #    if isinstance(i, int):
    #        del translasi_steps[i]

    # Pengurutan hasil translasi
    hasil_translasi.extend(translasi_steps)
    hasil_translasi.append("@enduml")
    print("\n".join(str(v) for v in hasil_translasi))
    return hasil_translasi

def generate(request, project_id, usecase_id):
    context = {
        'hasil_translasi' : translasi(usecase_id)
    }
    #raise Exception()
    return render(request, 'generate.html' , context)

