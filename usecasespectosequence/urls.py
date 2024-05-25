from django.urls import path
from . import views

app_name = 'usecasespectosequence'
urlpatterns = [
    path('home/<int:project_id>/usecase/<int:usecase_id>/form', views.form_tambah_usecasespec, name='form_tambah_usecasespec'),
    path('home/<int:project_id>/<int:usecase_id>/tambah_usecasespec', views.tambah_usecasespec, name='tambah_usecasespec'),
    path('home/<int:project_id>/<int:usecase_id>/tambah_step', views.form_tambah_step, name='form_tambah_step'),
    path('home/<int:project_id>/usecase/<int:usecase_id>/generate', views.generate, name='generate')
]