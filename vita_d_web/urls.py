"""
URL configuration for vita_d_web project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, re_path
from django.contrib.auth import views as auth_views
from django.urls import path
from . import views  # Aquí importas todas tus vistas del archivo views.py de la misma carpeta (.)
from . import authentication
urlpatterns = [
    
    path('', views.login_request, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('home/', views.home, name='home'),
    path('nuevo-paciente/', views.nuevo_paciente, name='nuevo_paciente'),
    path('historial-pacientes/', views.historial_pacientes, name='historial_pacientes'),
    path('nueva-prediccion/', views.nueva_prediccion, name='nueva_prediccion'),
    path('historial-predicciones/', views.historial_predicciones, name='historial_predicciones'),
    path('profile/', views.profile, name='profile'),  # Agrega esta línea
    path('faq/', views.faq, name='faq'),
    path('contact/', views.contact, name='contact'),
    path('cargar_modelo/', views.cargar_modelo, name='cargar_modelo'),
    path('hacer_prediccion/', views.hacer_prediccion, name='hacer_prediccion'),
    path('obtener_detalle_paciente/', views.obtener_detalle_paciente, name='obtener_detalle_paciente'),
    path('ruta/a/obtener_factores_riesgo', views.obtener_factores_riesgo, name='obtener_factores_riesgo'),
    path('predicciones/paciente/<int:paciente_id>/', views.predicciones_paciente_view, name='predicciones-paciente'),
    path('verificar-predicciones-previas/', views.verificar_predicciones_previas, name='verificar-predicciones-previas'),
]
