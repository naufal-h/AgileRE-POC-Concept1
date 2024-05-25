from django.db import models
from concept1.models import Project 

class Aktor(models.Model):
    nama_aktor = models.CharField(max_length=1024)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.nama_aktor
    
class Ucase(models.Model):
    use_case = models.CharField(max_length=200)
    aktor = models.ForeignKey(Aktor, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.use_case

class Spec(models.Model):
    deskripsi = models.TextField()
    flow = models.TextField()
    
    goal = models.TextField()
    awal = models.TextField()
    akhir = models.TextField()
    ucase = models.OneToOneField(Ucase, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.deskripsi
    
class Skenario(models.Model):
    step = models.TextField()
    spec = models.ForeignKey(Spec, on_delete=models.CASCADE, null=True)
    class Category(models.TextChoices):
        NORMAL = 'N', ('Normal')
        ALT = 'ALT', ('Alternative')
        EXC = 'EXC', ('Exception')
    
    category = models.CharField(max_length=3,
                                choices = Category.choices,
                                default= Category.NORMAL
    )
    
    def __str__(self):
        return self.step