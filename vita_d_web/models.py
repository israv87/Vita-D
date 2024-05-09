from django.db import models

class Usuario(models.Model):
    
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=255)
    email = models.EmailField(max_length=100)
    role = models.CharField(max_length=10)  # Considerar cambiar si no es un ENUM real
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'usuarios'

class Sesione(models.Model):
    user = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    token = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)
    expired = models.DateTimeField()

    class Meta:
        db_table = 'sesiones'

class Paciente(models.Model):
    edad = models.IntegerField()
    sexo = models.IntegerField()  # Considerar cambiar si no es un ENUM real
    imc = models.FloatField()
    cintCad = models.FloatField()
    grasaCorpL = models.FloatField()
    cigarrillos = models.IntegerField()
    alcohol = models.IntegerField()
    piel = models.IntegerField()
    diabetes = models.IntegerField()
    masaMuscL = models.FloatField()
    actFisica = models.IntegerField()
    trabajo = models.IntegerField()
    farmacos = models.IntegerField()
    protecSolar = models.IntegerField()
    expoDias = models.IntegerField()
    expoMinus = models.IntegerField()
    vitamD = models.FloatField()

    class Meta:
        db_table = 'pacientes'

class HistorialMedico(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    observaciones = models.TextField()
    fechaReg = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(Usuario, on_delete=models.CASCADE)

    class Meta:
        db_table = 'historial_medico'

class Prediccione(models.Model):
    fechaPred = models.DateTimeField(auto_now_add=True)
    deficit = models.CharField(max_length=2)
    prediction = models.FloatField()
    modelo = models.CharField(max_length=3)
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    user = models.ForeignKey(Usuario, on_delete=models.CASCADE)

    class Meta:
        db_table = 'predicciones'

class Metrica(models.Model):
    accuracy = models.FloatField()
    recall = models.FloatField()
    f1_score = models.FloatField()
    fecha_metrica = models.DateTimeField(auto_now_add=True)
    precision = models.FloatField()
    prediccion = models.ForeignKey(Prediccione, on_delete=models.CASCADE)

    class Meta:
        db_table = 'metricas'

class FactoresRiesgo(models.Model):
    variable = models.CharField(max_length=50)
    importancia = models.FloatField()
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)

    class Meta:
        db_table = 'factores_riesgo'