from django.db import models

class Project(models.Model):
    judul_project = models.CharField(max_length=100)
    deskripsi_project = models.TextField()
    img_path = models.TextField(max_length=455)
    
    def __str__(self):
        return self.judul_project
    
