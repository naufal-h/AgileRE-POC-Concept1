from django import forms
# import class Task dari file todo/models.py
from usecasespectosequence.models import Project, Usecase


# membuat class TaskForm untuk membuat task

class UsecaseForm(forms.ModelForm):
    class Meta:
        model = Usecase
        fields = ['usecase_name']

class UsecasespecForm(forms.ModelForm):
    class Meta:
        model = Usecase
        fields = ['usecase_name','actor','desc','postcon','postcon_object','precon','precon_object']



