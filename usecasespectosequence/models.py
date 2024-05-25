from django.db import models
from concept1.models import Project 
from ucase.models import Aktor, Ucase, Spec

# Create your models here.
class Usecase(models.Model):
    id = models.AutoField(primary_key=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    ucase = models.ForeignKey(Ucase, on_delete=models.CASCADE)
    usecase_name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    actor = models.CharField(max_length=200, blank=True)
    desc = models.CharField(max_length=200, blank=True)
    precon = models.CharField(max_length=200, blank=True)
    precon_object = models.CharField(max_length=200, blank=True)
    postcon = models.CharField(max_length=200, blank=True)
    postcon_object = models.CharField(max_length=200, blank=True)

class Steps(models.Model):
    step_id = models.AutoField(primary_key=True)
    spec = models.ForeignKey(Usecase, on_delete=models.CASCADE)
    is_alter = models.BooleanField()
    subject = models.CharField(max_length=200)
    activity = models.CharField(max_length=200)
    object = models.CharField(max_length=200)

    def __str__(self):
        return self.subject
