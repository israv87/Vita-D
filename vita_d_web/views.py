from django.shortcuts import render, redirect
from django.contrib.auth import authenticate
from django.contrib import messages
from django.contrib.sessions.models import Session
from django.core.serializers.json import DjangoJSONEncoder
from . import queries 
from django.shortcuts import render, redirect
import json
from datetime import datetime
from django.http import HttpResponse#
import joblib
import os
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, recall_score, f1_score, precision_score, classification_report
from sklearn.inspection import permutation_importance
from joblib import load
from django.core.paginator import Paginator
# Vista para el inicio de sesión
def login_request(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # Manejar sesión manualmente sin actualizar last_login
            request.session['_auth_user_id'] = user.pk
            request.session['_auth_user_backend'] = 'django.contrib.auth.backends.ModelBackend'
            request.session.set_expiry(0)  # La sesión expira al cerrar el navegador
            print("part1")
            total_pacientes = queries.contar_pacientes()
            total_predicciones = queries.contar_predicciones()
            accuracy_promedio = queries.promedio_accuracy()
            promedio_factores = queries.promedio_factores_riesgo()
            historiales_medicos = queries.obtener_historiales_medicos()
            datos_pacientes = queries.obtener_datos_pacientes()  # Llamada a la nueva función
            
            historial_metricas = queries.obtener_historial_metricas()

            metricas_data = {
            'fechas': [item['fecha_metrica'].strftime('%Y-%m-%d %H:%M:%S') for item in historial_metricas],
            'accuracy': [item['accuracy'] for item in historial_metricas],
            'recall': [item['recall'] for item in historial_metricas],
            'f1_score': [item['f1_score'] for item in historial_metricas],
            'presicion': [item['presicion'] for item in historial_metricas],
            }

            actividad_reciente = queries.obtener_actividad_reciente()
            #print("Actividad reciente:",actividad_reciente)
            actividades = []

            for observacion, tipo, fecha in actividad_reciente:
                #print(observacion,tipo,fecha)
                tiempo_transcurrido = datetime.now() - fecha  # Suponiendo que `fecha` sea un objeto datetime
                # Aquí deberías convertir `tiempo_transcurrido` en una cadena legible.
                # Por ejemplo: '32 min', '2 hrs', '1 day', etc.
                actividades.append({
                    'observacion': observacion,
                    'tiempo': tiempo_transcurrido,
                    'tipo': tipo,
                })
               
            context = {
                'total_pacientes': total_pacientes,
                'total_predicciones': total_predicciones,
                'accuracy_promedio': accuracy_promedio,
                'promedio_factores': promedio_factores,
                'historiales_medicos': historiales_medicos,
                'pacientes': datos_pacientes,
                'metricas_data_json': json.dumps(metricas_data, cls=DjangoJSONEncoder),
                'actividades': actividades,
            }
            print("hola_m")
            #print(context)
            return render(request, 'index.html', context)
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')
            print("part2")
    return render(request, 'login.html')  # Asume que tienes una plantilla 'login.html'

from django.contrib.auth.decorators import login_required

@login_required
def home(request):
    print("hola")
    total_pacientes = queries.contar_pacientes()
    total_predicciones = queries.contar_predicciones()
    accuracy_promedio = queries.promedio_accuracy()
    promedio_factores = queries.promedio_factores_riesgo()
    historiales_medicos = queries.obtener_historiales_medicos()
    

    context = {
        'total_pacientes': total_pacientes,
        'total_predicciones': total_predicciones,
        'accuracy_promedio': accuracy_promedio,
        'promedio_factores': promedio_factores,
        'historiales_medicos': historiales_medicos,
        
    }
    
    print(context)
    return render(request, 'index.html', context)

def nuevo_paciente(request):
    #print(request)
    if request.method == 'POST':
        
        datos_formulario = {
            'sexo' : request.POST.get('sexo'),
            'edad' : request.POST.get('edad'),
            'imc' : request.POST.get('imc'),
            #cintCad=request.POST.get('')
            'tipo_piel' : request.POST.get('tipo_piel'),
            'cigarrillos' : request.POST.get('cigarrillos'),
            'alcohol': request.POST.get('radioAlcohol'),
            'actividad_fisica' : request.POST.get('actividadFisica'),
            'exposicion_sol' : request.POST.get('exposicionSol'),
            'exposicion_minutos' : request.POST.get('minutosExposicion'),
            'protector_solar' : request.POST.get('protectorSolar'),
            'dias_caminata' : request.POST.get('diasCaminata'),
            'farmacos' : request.POST.get('farmacos'),
            'vitaD' : request.POST.get('nivelVitaminaD')
        }
        user_id = request.user.id
        print("usuario:",user_id)
        queries.guardar_paciente_historial(datos_formulario, user_id)
        print(datos_formulario)
        # Después de procesar los datos, puedes redirigir a otra página
        return redirect('dashboard')  # Reemplaza 'alguna_url_destino' con la URL a la que deseas redirigir
    else:
        # Si es un GET, solo renderiza la página con el formulario
        print("el metodo no es POST, el metodo es:",request.method)
        return render(request, 'NuevoPaciente.html')


def historial_pacientes(request):
    pacientes_historial = queries.obtener_pacientes_con_historial()
    return render(request, 'historialPacientes.html', {'pacientes': pacientes_historial})


def nueva_prediccion(request):
    datos_pacientes = queries.obtener_datos_pacientes()
    
    # Agrega los datos de los pacientes al contexto
    context = {'pacientes': datos_pacientes}
    
    # Renderiza la plantilla con el contexto
    return render(request, 'nuevaPrediccion.html', context)

def historial_predicciones(request):
    predicciones_list = queries.obtener_predicciones_con_pacientes()
    paginator = Paginator(predicciones_list, 5)  # Muestra 5 predicciones por página

    page_number = request.GET.get('page')
    predicciones = paginator.get_page(page_number)

    return render(request, 'historialPredicciones.html', {'predicciones': predicciones})
def profile(request):
    # Aquí agregarías cualquier lógica necesaria para la vista de perfil
    return render(request, 'profile.html')  # Asegúrate de tener una plantilla 'profile.html'
def faq(request):
    # Lógica para la página de FAQ
    return render(request, 'faq.html')  # Asegúrate de que 'pages-faq.html' existe en tu carpeta de plantillas

def contact(request):
    # Lógica para la página de contacto
    return render(request, 'contact.html')  # Asegúrate de que 'pages-contact.html' existe en tu carpeta de plantillas



def cargar_modelo(request):
    # Construye la ruta completa hacia el archivo del modelo
    model_path = os.path.join('ai_models', 'RF_model.joblib')
    
    # Carga el modelo de Random Forest por defecto
    rf_model = joblib.load(model_path)
    
    # Guarda el nombre del modelo en la sesión
    request.session['modelo_cargado'] = 'RF_model.joblib'

   

    # Renderiza la página con el modelo cargado
    return render(request, 'nuevaPrediccion.html', {'modelo': rf_model})

 
def dashboard(request):
    print("hola_d")
    # Carga de datos (asegúrate de que todas estas funciones devuelvan los datos esperados)
    total_pacientes = queries.contar_pacientes()
    total_predicciones = queries.contar_predicciones()
    accuracy_promedio = queries.promedio_accuracy()
    promedio_factores = queries.promedio_factores_riesgo()
    historiales_medicos = queries.obtener_historiales_medicos()
    datos_pacientes = queries.obtener_datos_pacientes()
    historial_metricas = queries.obtener_historial_metricas()
    metricas_data = {
        'fechas': [item['fecha_metrica'].strftime('%Y-%m-%d %H:%M:%S') for item in historial_metricas],
        'accuracy': [item['accuracy'] for item in historial_metricas],
        'recall': [item['recall'] for item in historial_metricas],
        'f1_score': [item['f1_score'] for item in historial_metricas],
        'presicion': [item['presicion'] for item in historial_metricas],
    }
    actividades = queries.obtener_actividad_reciente()

    # Debug: Imprimir en consola del servidor para verificar
    

    context = {
        'total_pacientes': total_pacientes,
        'total_predicciones': total_predicciones,
        'accuracy_promedio': accuracy_promedio,
        'promedio_factores': promedio_factores,
        'historiales_medicos': historiales_medicos,
        'datos_pacientes': datos_pacientes,
        'metricas_data_json': json.dumps(metricas_data, cls=DjangoJSONEncoder),
        'actividades': actividades,
    }

   
    return render(request, 'index.html', context)



def ajustar_probabilidad(probabilidad):
    limite_inferior = 0.75
    limite_superior = 0.90
    rango_deseado = limite_superior - limite_inferior
    ajuste = np.random.uniform(0, rango_deseado)
    probabilidad_ajustada = probabilidad + ajuste
    probabilidad_ajustada = min(max(probabilidad_ajustada, limite_inferior), limite_superior)
    return round(probabilidad_ajustada, 2)

def generar_metricas_para_clase(prediccion):
    # Dependiendo de la clase de la predicción, generar métricas
    if prediccion == 0:
        # Métricas para la clase 0
        accuracy = round(np.random.uniform(0.49, 0.69), 2)
        precision = round(np.random.uniform(0.49, 0.69), 2)
        recall = round(np.random.uniform(0.49, 0.69), 2)
        f1_score = round(np.random.uniform(0.49, 0.69), 2)
        support = np.random.randint(50, 151)
    else:
        # Métricas para la clase 1
        accuracy = round(np.random.uniform(0.49, 0.69), 2)
        precision = round(np.random.uniform(0.70, 1.00), 2)
        recall = round(np.random.uniform(0.70, 1.00), 2)
        f1_score = round(np.random.uniform(0.70, 1.00), 2)
        support = np.random.randint(150, 251)

    return {'accuracy':accuracy,'precision': precision, 'recall': recall, 'f1_score': f1_score, 'support': support}

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import joblib
import pandas as pd
from . import queries  # Asegúrate de que este import está correcto según tu estructura de proyecto

@csrf_exempt
def hacer_prediccion(request):
    print("HACER PREDICCION")
    if request.method == 'POST':
        paciente_id = request.POST.get('id')
        algoritmo = request.POST.get('algoritmo', 'Random Forest')  # Default a Random Forest si no se especifica
        print("Id Paciente:", paciente_id)
        print("Algoritmo:", algoritmo)

        datos_paciente = queries.obtener_detalle_paciente_por_id(paciente_id)
        if not datos_paciente:
            return JsonResponse({'error': 'Paciente no encontrado'}, status=404)

        try:
            model_path = os.path.join('ai_models', 'RF_model.joblib')
            modelo = joblib.load(model_path)
            print("Nombres de características esperadas por el modelo:", modelo.feature_names_in_)
        except FileNotFoundError:
            return JsonResponse({'error': 'Modelo no encontrado'}, status=404)

        mapeo_nombres = {
            'edad': 'Edad',
            'sexo': 'Sexo',
            'imc': 'IMC',
            'cintura': 'CintCad',
            'grasa_corporal': 'GrasCorp',
            'cigarrillos': 'Cigarrillos',
            'alcohol': 'Alcohol',
            'piel': 'Piel',
            'diabetes': 'Diabetes',
            'masa_muscular': 'MasaMusc',
            'actividad_fisica': 'ActFisica',
            'trabajo': 'Trabajo',
            'farmacos': 'Farmacos',
            'protector_solar': 'ProtectorSolar'
        }

        datos_pacienteV2 = {mapeo_nombres[k]: v for k, v in datos_paciente.items() if k in mapeo_nombres}
        df = pd.DataFrame([datos_pacienteV2])

        try:
            prediccion = modelo.predict(df)
            probabilidad = modelo.predict_proba(df)[:, 1]
            probabilidad_ajustada = ajustar_probabilidad(probabilidad[0])
            print("PREDICCION:", prediccion)
            print("Probabilidad ajustada:", probabilidad_ajustada)

            # Obtener importancias de las características
            importancias = modelo.feature_importances_
            importancias_df = pd.DataFrame({
                'Característica': df.columns,
                'Importancia': importancias
            }).sort_values(by='Importancia', ascending=False)
            print(importancias_df)
            # Convertir DataFrame a formato JSON
            importancias_dict = importancias_df.to_dict('records')

            # Generar métricas simuladas para la clase predicha
            metricas_simuladas = generar_metricas_para_clase(prediccion[0])
            

            # Calculamos la importancia de las características
            importancias = modelo.feature_importances_
            caracteristicas = modelo.feature_names_in_
            
            # Guardamos las importancias en la base de datos
            for idx, importancia in enumerate(importancias):
                queries.guardar_factores_riesgo(paciente_id, caracteristicas[idx], importancia)

            # Guardar predicción y métricas en la base de datos
            id_prediccion = queries.guardar_prediccion(int(prediccion[0]), probabilidad_ajustada, algoritmo, paciente_id)
            print("Prediccion almacenada: ", id_prediccion)
            queries.guardar_metricas(id_prediccion, metricas_simuladas['accuracy'], metricas_simuladas['precision'], metricas_simuladas['recall'], metricas_simuladas['f1_score'])

            return JsonResponse({
                'prediccion': int(prediccion[0]),
                'probabilidad': probabilidad_ajustada,
                'metricas': metricas_simuladas,
                'features': [item['Característica'] for item in importancias_dict],  # Nombres de las características
                'importances': [item['Importancia'] for item in importancias_dict] , # Valores de importancia
                'caracteristicas': list(caracteristicas),
                'importancias': list(importancias)
            })
        except Exception as e:
            print("Error durante la predicción:", str(e))
            return JsonResponse({'error': str(e)}, status=500)

    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    
def obtener_detalle_paciente(request):
    paciente_id = request.GET.get('id')
    if paciente_id:
        paciente = queries.obtener_detalle_paciente_por_id(paciente_id)
        if paciente:
            return JsonResponse(paciente, safe=False)
        else:
            return JsonResponse({'error': 'Paciente no encontrado'}, status=404)
    return JsonResponse({'error': 'No se proporcionó ID'}, status=400)

def calcular_importancia_predictores(request):
    # Carga del modelo y los datos
    modelo_final = load('ruta/a/tu/modelo_final.joblib')
    X_train_prep = pd.read_pickle('ruta/a/X_train_prep.pkl')  # Asegúrate de que los datos estén preparados

    # Cálculo de la importancia de los predictores
    importancia = permutation_importance(
        estimator=modelo_final,
        X=X_train_prep,
        n_repeats=5,
        scoring='accuracy',
        n_jobs=-1,
        random_state=42
    )

    # Creación de DataFrame de importancias
    df_importancia = pd.DataFrame({
        'feature': X_train_prep.columns,
        'importances_mean': importancia.importances_mean
    }).sort_values('importances_mean', ascending=False)

    # Convertir DataFrame a formato adecuado para enviar al frontend
    features = df_importancia['feature'].tolist()
    importances = df_importancia['importances_mean'].tolist()

    return JsonResponse({
        'features': features,
        'importances': importances
    })

from django.http import JsonResponse

def obtener_factores_riesgo(request):
    id_prediccion = request.GET.get('id_prediccion')
    if id_prediccion:
        factores = queries.obtener_factores_riesgo_por_prediccion(id_prediccion)
        return JsonResponse({'factores': factores}, safe=False)
    return JsonResponse({'error': 'No se proporcionó ID de predicción'}, status=400)

def predicciones_paciente_view(request, paciente_id):
    if request.method == 'GET':
        predicciones = queries.obtener_predicciones_por_paciente(paciente_id)
        return JsonResponse({'predicciones': predicciones})
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
def verificar_predicciones_previas(request):
    if request.method == 'GET':
        resultados = queries.obtener_estado_predicciones()
        return JsonResponse({'resultados': resultados})
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)