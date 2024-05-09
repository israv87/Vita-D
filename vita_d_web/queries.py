from django.db import connection

# Devuelve todos los registros como un diccionario.
def dictfetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

def contar_pacientes():
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM pacientes")
        count = cursor.fetchone()[0]
    return count

def contar_predicciones():
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM predicciones")
        count = cursor.fetchone()[0]
    return count

def promedio_accuracy():
    with connection.cursor() as cursor:
        cursor.execute("SELECT AVG(accuracy) FROM metricas")
        promedio = cursor.fetchone()[0]
        if promedio is not None:
            promedio = round(promedio, 2)  # Redondea a dos decimales
        
    return promedio
def promedio_factores_riesgo():
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT AVG(contador) FROM (
                SELECT COUNT(*) as contador 
                FROM factoresRiesgo 
                GROUP BY idPaciente
            ) as conteos
        """)
        promedio = cursor.fetchone()[0]
    return promedio

def obtener_historiales_medicos():
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM historialMedico")
        historiales = dictfetchall(cursor)
    return historiales

def obtener_datos_pacientes():
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT *
            FROM pacientes
        """)
        return dictfetchall(cursor)

def obtener_historial_metricas():
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT `accuracy`, `recall`, `f1_score`, `presicion`, `fecha_metrica`
            FROM `metricas`
            ORDER BY `fecha_metrica` ASC
        """)
        columns = [col[0] for col in cursor.description]
        return [
            dict(zip(columns, row))
            for row in cursor.fetchall()
        ]
def obtener_actividad_reciente():
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT observaciones, tipo, fechaReg
            FROM vita_db.historialmedico
            ORDER BY fechaReg DESC
            LIMIT 5  # o el número de eventos recientes que deseas mostrar
        """)
        return cursor.fetchall()

def guardar_paciente_historial(datos, user_id):
    with connection.cursor() as cursor:
        # Guardar en la tabla de pacientes
        cursor.execute("""
            INSERT INTO vita_db.pacientes (edad, sexo, imc, cintCad,grasaCorpl,cigarrillos,alcohol,
                       piel, diabetes,masaMusc,actFisica,trabajo,farmacos,protectorSolar,expoDias,
                       expoMinutos,vitaminaD)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s,%s, %s, %s,%s,%s)
        """, [datos['edad'], datos['sexo'], datos['imc'], '0', '0',datos['cigarrillos'], datos['alcohol'], 
              datos['tipo_piel'],'0','0', datos['actividad_fisica'],'0', datos['farmacos'],
              datos['protector_solar'],datos['exposicion_sol'],datos['exposicion_minutos'],
              datos['vitaD']])
        id_paciente = cursor.lastrowid

        # Guardar en el historial médico
        cursor.execute("""
            INSERT INTO vita_db.historialMedico (observaciones, fechaReg, tipo, idPaciente, idUser)
            VALUES ('Ninguno', NOW(), 'registro', %s, '2')
        """, [id_paciente])


from django.db import connection

def obtener_detalle_paciente_por_id(paciente_id):
    with connection.cursor() as cursor:
        query = """
        SELECT id, edad, sexo, imc, cintCad, grasaCorpl, cigarrillos, alcohol, piel, diabetes, 
               masaMusc, actFisica, trabajo, farmacos, protectorSolar, expoDias, expoMinutos, vitaminaD
        FROM vita_db.pacientes
        WHERE id = %s
        """
        cursor.execute(query, [paciente_id])
        row = cursor.fetchone()

        if row:
            return {
                'id': row[0],
                'edad': row[1],
                'sexo': row[2],
                'imc': row[3],
                'cintura': row[4],
                'grasa_corporal': row[5],
                'cigarrillos': row[6],
                'alcohol': row[7],
                'piel': row[8],
                'diabetes': row[9],
                'masa_muscular': row[10],
                'actividad_fisica': row[11],
                'trabajo': row[12],
                'farmacos': row[13],
                'protector_solar': row[14],
                'exposicion_dias': row[15],
                'exposicion_minutos': row[16],
                'vitamina_d': row[17]
            }
        else:
            return None
# queries.py

def guardar_prediccion(prediccion,probabilidad, algoritmo, paciente_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO vita_db.predicciones (fechaPred,deficit,probabilidad, modelo, idPaciente, idUser)
            VALUES (NOW(),%s, %s, %s , %s,"1")
        """, [prediccion,probabilidad, algoritmo, paciente_id])
        return cursor.lastrowid  # Devuelve el ID de la fila insertada

def guardar_metricas(id_prediccion, accuracy, precision, recall, f1):
    with connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO vita_db.metricas (accuracy, recall, f1_score, fecha_metrica, presicion, idPrediccion)
            VALUES (%s, %s, %s, NOW(), %s, %s)
        """, [accuracy, recall, f1, precision, id_prediccion])

def obtener_pacientes_con_historial():
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT p.id, p.edad, p.sexo, p.imc, p.cintCad, p.grasaCorpl, p.cigarrillos, p.alcohol,
                   p.actFisica, p.vitaminaD, h.observaciones, h.fechaReg
            FROM vita_db.pacientes p
            JOIN historialMedico h ON p.id = h.idPaciente
            ORDER BY h.fechaReg DESC
        """)
        return dictfetchall(cursor)
    
def obtener_predicciones_con_pacientes():
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT p.id,p.edad, p.sexo, p.imc, p.cintCad, p.grasaCorpl, p.piel, pr.deficit, pr.modelo, pr.fechaPred
            FROM pacientes p
            JOIN predicciones pr ON p.id = pr.idPaciente
            ORDER BY pr.fechaPred DESC
        """)
        return dictfetchall(cursor)

def guardar_factores_riesgo(id_paciente, variable, importancia):
    with connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO factoresRiesgo (idPaciente, variable, importancia)
            VALUES (%s, %s, %s)
        """, [id_paciente, variable, importancia])

def obtener_factores_riesgo_por_prediccion(id_prediccion):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT DISTINCT variable, importancia
            FROM factoresRiesgo
            WHERE idPaciente = %s
            ORDER BY variable, importancia DESC
        """, [id_prediccion])
        return dictfetchall(cursor)
    
def get_medical_history_activities(user_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT fechaReg AS activity_date, observaciones AS description
            FROM historialMedico
            WHERE idUser = %s
            ORDER BY fechaReg DESC;
        """, [user_id])
        return cursor.fetchall()    
    
def obtener_predicciones_por_paciente(paciente_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, fechaPred, deficit, probabilidad
            FROM predicciones
            WHERE idPaciente = %s
            ORDER BY fechaPred DESC;
        """, [paciente_id])
        result = cursor.fetchall()
    return [{
        'id': row[0],
        'fechaPred': row[1].strftime('%Y-%m-%d %H:%M:%S'),  # Formatear la fecha
        'deficit': row[2],
        'probabilidad': row[3]
    } for row in result]
def obtener_estado_predicciones():
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT p.id, COUNT(pr.id) > 0 AS tiene_predicciones
            FROM pacientes p
            LEFT JOIN predicciones pr ON p.id = pr.idPaciente
            GROUP BY p.id;
        """)
        result = cursor.fetchall()
    return [{'paciente_id': row[0], 'tiene_predicciones': bool(row[1])} for row in result]