from django.urls import path
from . import views

app_name = 'ucase'
urlpatterns = [
    path('input_diagram/',views.InputDiagram,name='input_diagram'),
    path('input_spec/<int:ucase_id>',views.InputSpec,name='input_spec'),
    path('diagram/<int:pk>', views.DiagramPage, name='diagram'),
    path('spec/<int:pk>', views.specpage, name='spec'),
]
