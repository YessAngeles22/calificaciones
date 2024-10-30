# -*- coding: utf-8 -*-

import firebase_admin
from firebase_admin import credentials, firestore
from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)
cred = credentials.Certificate('C:\\evaluacion\\planevaluacion-803ca-firebase-adminsdk-l70kg-80b3dc84ec.json')
firebase_admin.initialize_app(cred)

db = firestore.client()

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/agregar_tareas", methods=['GET', 'POST'])
def agregar_tareas():
    if request.method == 'POST':
        nombre_tarea = request.form['nombre_tarea']
        materia = request.form['materia']
        grado = request.form['grado']  # Captura el grado
        grupo = request.form['grado_grupo']  # Captura el grupo

        tareas_ref = db.collection('tareas')
        tareas_ref.add({
            'nombre_tarea': nombre_tarea,
            'materia': materia,
            'grado': grado,  # Almacena el grado
            'grupo': grupo   # Almacena el grupo
        })
        return redirect(url_for('agregar_tareas'))

    materias = obtener_materias()
    grupos = obtener_grupos()
    grados = [doc.to_dict()['grado'] for doc in db.collection('grupos').stream()]  # Asegúrate de obtener los grados
    tareas = obtener_tareas()
    
    return render_template('agregar_tarea.html', materias=materias, grupos=grupos, grados=grados, tareas=tareas)

    materias = obtener_materias()
    grupos = obtener_grupos()
    tareas = obtener_tareas()
    print(f'Tareas para mostrar: {tareas}')  # Debugging
    return render_template('agregar_tarea.html', materias=materias, grupos=grupos, tareas=tareas)

def obtener_materias():
    materias_ref = db.collection('materias')
    materias = []
    for doc in materias_ref.stream():
        materia_data = doc.to_dict()
        materias.append({
            'nombre': materia_data.get('nombre', ''),
            'codigo': materia_data.get('codigo', ''),
            'generacion': materia_data.get('generacion', '')
        })
    return materias

def obtener_grupos():
    grupos_ref = db.collection('grupos')
    return [doc.to_dict()['grupo'] for doc in grupos_ref.stream()]

def obtener_tareas():
    tareas_ref = db.collection('tareas')
    return [doc.to_dict() for doc in tareas_ref.stream()]

@app.route('/agregar_materia', methods=['GET', 'POST'])
def agregar_materia():
    if request.method == 'POST':
        nombre_materia = request.form['nombre']
        codigo_materia = request.form['codigo']
        generacion_materia = request.form['generacion']

        db.collection('materias').add({
            'nombre': nombre_materia,
            'codigo': codigo_materia,
            'generacion': generacion_materia
        })
        return redirect(url_for('agregar_materia'))

    materias = [doc.to_dict() for doc in db.collection('materias').stream()]
    return render_template('agregar_materia.html', materias=materias)

@app.route('/agregar_alumno', methods=['GET', 'POST'])
def agregar_alumno():
    if request.method == 'POST':
        nombre = request.form['nombre']
        matricula = request.form['matricula']
        grado = request.form['grado']
        grupo = request.form['grupo']
        materia = request.form['materia']

        db.collection('alumnos').add({
            'nombre': nombre,
            'matricula': matricula,
            'grado': grado,
            'grupo': grupo,
            'materia': materia
        })
        return redirect(url_for('index'))

    grados = [doc.to_dict()['grado'] for doc in db.collection('grupos').stream()]
    grupos = [doc.to_dict()['grupo'] for doc in db.collection('grupos').stream()]
    materias = [doc.to_dict()['nombre'] for doc in db.collection('materias').stream()]

    return render_template('agregar_alumno.html', grupos=grupos, materias=materias, grados=grados)

@app.route('/agregar_grupo', methods=['GET', 'POST'])
def agregar_grupo():
    if request.method == 'POST':
        grado = request.form['grado']
        grupo = request.form['grupo']
        generacion = request.form['generacion']

        db.collection('grupos').add({
            'grado': grado,
            'grupo': grupo,
            'generacion': generacion
        })
        return redirect(url_for('agregar_grupo'))

    grupos = db.collection('grupos').stream()
    grupos_lista = [{'grado': doc.to_dict()['grado'], 'grupo': doc.to_dict()['grupo'], 'generacion': doc.to_dict()['generacion']} for doc in grupos]

    return render_template('agregar_grupo.html', grupos=grupos_lista)

@app.route('/evaluar', methods=['GET', 'POST'])
def evaluar():
    if request.method == 'POST':
        nombre_alumno = request.form.get('nombre_alumno')
        grupo = request.form.get('grupo')  # Captura el grupo
        materia = request.form.get('materia')
        calificacion = request.form.get('calificacion')
        tarea = request.form.get('tarea')

        print(f"Datos recibidos: Nombre Alumno: {nombre_alumno}, Grupo: {grupo}, Materia: {materia}, Calificacion: {calificacion}, Tarea: {tarea}")

        # Asegúrate de que todos los datos estén presentes
        if not (nombre_alumno and grupo and materia and calificacion and tarea):
            return "Datos faltantes", 400

        # Guarda los datos en la base de datos
        db.collection('evaluaciones').add({
            'nombre_alumno': nombre_alumno,
            'grupo': grupo,  # Guarda el grupo aquí
            'materia': materia,
            'calificacion': calificacion,
            'tarea': tarea
        })
        return redirect(url_for('index'))

    # Código para el método GET
    alumnos = [doc.to_dict()['nombre'] for doc in db.collection('alumnos').stream()]
    materias = [doc.to_dict()['nombre'] for doc in db.collection('materias').stream()]
    grupos = obtener_grupos()
    tareas = obtener_tareas()

    return render_template('evaluar.html', alumnos=alumnos, materias=materias, grupos=grupos, tareas=tareas)


    # Código para el método GET
    alumnos = [doc.to_dict()['nombre'] for doc in db.collection('alumnos').stream()]
    materias = [doc.to_dict()['nombre'] for doc in db.collection('materias').stream()]
    grupos = obtener_grupos()
    tareas = obtener_tareas()

    return render_template('evaluar.html', alumnos=alumnos, materias=materias, grupos=grupos, tareas=tareas)
@app.route('/calificaciones', methods=['GET'])
def calificaciones():
    # Obtener las calificaciones de la base de datos
    evaluaciones = db.collection('evaluaciones').stream()
    
    calificaciones_por_materia = {}
    for eval in evaluaciones:
        data = eval.to_dict()
        materia = data['materia']
        
        if materia not in calificaciones_por_materia:
            calificaciones_por_materia[materia] = []
        calificaciones_por_materia[materia].append(data)

    return render_template('calificaciones.html', calificaciones=calificaciones_por_materia)
if __name__ == '__main__':
    import os
    HOST = os.environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(os.environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    app.run(HOST, PORT)
