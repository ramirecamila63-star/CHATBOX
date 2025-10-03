#pip install virtualenv
#python -m venv entorno1
#cd chatbot
#cd entorno1 
#.\Scripts\Activate

#cd chatbot
#source ./entorno1/bin/activate
#python main.py

from flask import Flask, render_template, request, redirect, url_for, g, session, jsonify
from datetime import datetime, timedelta
import sqlite3
from flask_session import Session  # Importar Flask-Session

# Reemplaza 'TU_API_KEY' con tu clave real o usa una variable de entorno
import os
import google.generativeai as genai
import markdown

genai.configure(api_key="AIzaSyDM1oeUQrrkE_lhcZwHtrfS_eRMjrnWy2U") 
model = genai.GenerativeModel("gemini-pro")

MAX_HISTORY = 4

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_aqui'  # Clave secreta para las sesiones

# Configuración de sesiones
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)  # Inicializar Flask-Session

DATABASE = 'base.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.before_request
def before_request():
    # Si la página se refresca, limpiar la sesión del chat
    if request.endpoint and request.endpoint != 'procesar_chat_moto' and request.endpoint != 'verificar_sesion_chat':
        # No limpiar la sesión si es una petición AJAX del chat
        if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Limpiar solo las variables de sesión del chat, no toda la sesión
            if 'chat_moto_usuario' in session:
                session.pop('chat_moto_usuario', None)
            if 'chat_moto_paso' in session:
                session.pop('chat_moto_paso', None)
            if 'chat_moto_datos' in session:
                session.pop('chat_moto_datos', None)

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route("/base")
def base():
    return render_template('base.html')

@app.route('/mision', methods=['GET', 'POST'])
def mision():
    if request.method == 'POST':
        codigo = request.form.get('codigo')
        descripcion = request.form.get('descripcion')
       
        db = get_db()
        cursor = db.cursor()
        try:
            
            cursor.execute("INSERT INTO carrera (codigo, descripcion) VALUES (?, ?)", (codigo, descripcion))
            db.commit()
            print(f"Programa guardado: Código {codigo}, Descripción: {descripcion}")
            
            return redirect(url_for('respuesta', codigo=codigo, descripcion=descripcion))
        except sqlite3.IntegrityError as e:
            print(f"Error: {e}")
            return render_template('mision.html', error="El código o la descripción ya existen")
        except Exception as e:
            print(f"Error inesperado: {e}")
            return render_template('mision.html', error="Error al guardar el programa")
    else:
        return render_template('mision.html')

@app.route("/vision", methods=['GET', 'POST'])
def vision():
    if request.method == 'POST':
        codigo = request.form.get('codigo')
        descripcion = request.form.get('descripcion')
        
        print("="*50)
        print("DATOS RECIBIDOS EN VISIÓN (POST):")
        print(f"Código del programa: {codigo}")
        print(f"Descripción del programa: {descripcion}")
        print("="*50)

        return render_template('vision.html',
                             codigo=codigo,
                             descripcion=descripcion,
                             from_form=True)
    return render_template('vision.html', from_form=False)

@app.route("/programas", methods=['GET'])
def programas():
    return render_template('programas.html')

@app.route("/lista_carreras")
def lista_carreras():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM carrera")
    programas = cursor.fetchall()
    return render_template('lista_carreras.html', programas=programas)

@app.route("/respuesta")
def respuesta():
    codigo = request.args.get('codigo')
    descripcion = request.args.get('descripcion')
    
    return render_template('respuesta.html', codigo=codigo, descripcion=descripcion)

@app.route("/editar_carrera/<string:codigo>", methods=['GET', 'POST'])  # Cambiado a string y codigo
def editar_carrera(codigo):
    db = get_db()
    cursor = db.cursor()
    
    if request.method == 'POST':
        nueva_descripcion = request.form.get('descripcion')
        try:
            cursor.execute("UPDATE carrera SET descripcion = ? WHERE codigo = ?", (nueva_descripcion, codigo))
            db.commit()
            print(f"Programa actualizado: Código {codigo}, Nueva descripción: {nueva_descripcion}")
            return redirect(url_for('lista_carreras'))
        except Exception as e:
            print(f"Error al actualizar: {e}")
            return render_template('editar_carrera.html', codigo=codigo, error="Error al actualizar el programa")
    else:
        cursor.execute("SELECT * FROM carrera WHERE codigo = ?", (codigo,))
        programa = cursor.fetchone()
        return render_template('editar_carrera.html', programa=programa)

@app.route("/eliminar_carrera/<string:codigo>")  # Cambiado a string y codigo
def eliminar_carrera(codigo):
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM carrera WHERE codigo = ?", (codigo,))
        db.commit()
        print(f"Programa eliminado: Código {codigo}")
    except Exception as e:
        print(f"Error al eliminar: {e}")
    return redirect(url_for('lista_carreras'))

@app.route("/predic", methods=["POST"])
def predic():
    prompt = request.form.get("prompt")
    if not prompt:
        return render_template("chat.html", error="Por favor, ingresa una pregunta")
    
    try:
        # Generar respuesta con Gemini
        response = model.generate_content(prompt)
        # Convertir la respuesta de Markdown a HTML
        response_html = markdown.markdown(response.text)
        return render_template("chat.html", prompt=prompt, response=response_html)
    except Exception as e:
        return render_template("chat.html", error=f"Error al generar respuesta: {str(e)}")

@app.route("/predict", methods=['GET', 'POST'])
def predict():
    if request.method == "GET":
        return render_template('chat.html')
    else:
        return redirect(url_for('predic'))
    

@app.route("/procesar_chat_moto", methods=["POST"])
def procesar_chat_moto():
    mensaje = request.form.get("mensaje", "").strip().lower()
    
    # Comandos especiales que funcionan en cualquier momento
    if mensaje in ["volver", "atras", "regresar"]:
        # Volver al menú principal si el usuario ya está registrado
        if session.get('chat_moto_usuario'):
            session['chat_moto_paso'] = 'menu_principal'
            return jsonify({"respuesta": "Has vuelto al menú principal. ¿Qué deseas hacer?\n1. Agendar cita\n2. Ver citas agendadas\n3. Salir"})
        else:
            return jsonify({"respuesta": "No puedes volver porque aún no has iniciado sesión. Por favor, proporciona tu nombre y documento."})
    
    elif mensaje in ["salir", "cerrar", "terminar"]:
        # Reiniciar la sesión del chat
        if 'chat_moto_usuario' in session:
            session.pop('chat_moto_usuario')
        if 'chat_moto_paso' in session:
            session.pop('chat_moto_paso')
        if 'chat_moto_datos' in session:
            session.pop('chat_moto_datos')
        return jsonify({"respuesta": "Sesión cerrada. ¡Hola! Soy el asistente para agendar citas de mantenimiento de motos. ¿En qué puedo ayudarte?"})
    
    elif mensaje in ["reiniciar", "empezar de nuevo", "reset"]:
        # Reiniciar completamente la conversación
        if 'chat_moto_usuario' in session:
            session.pop('chat_moto_usuario')
        if 'chat_moto_paso' in session:
            session.pop('chat_moto_paso')
        if 'chat_moto_datos' in session:
            session.pop('chat_moto_datos')
        return jsonify({"respuesta": "Conversación reiniciada. Por favor, proporciona tu nombre y documento para comenzar."})
    
    elif mensaje in ["ayuda", "comandos", "help"]:
        return jsonify({"respuesta": "Comandos disponibles:\n- 'volver': Volver al menú anterior\n- 'reiniciar': Reiniciar la conversación\n- 'salir': Cerrar la sesión\n- 'ayuda': Mostrar esta ayuda"})
    
    # Inicializar variables de sesión si no existen
    if 'chat_moto_usuario' not in session:
        session['chat_moto_usuario'] = None
        session['chat_moto_paso'] = 'inicio'
        session['chat_moto_datos'] = {}
    
    # Procesar según el paso actual
    if session['chat_moto_paso'] == 'inicio':
        if mensaje and any(palabra in mensaje for palabra in ['hola', 'buenos dias', 'buenas tardes', 'buenas noches']):
            session['chat_moto_paso'] = 'pedir_nombre'
            return jsonify({"respuesta": "¡Hola! Para agendar una cita de mantenimiento, necesito tu nombre completo:"})
        else:
            return jsonify({"respuesta": "¡Hola! Soy el asistente para agendar citas de mantenimiento de motos. ¿En qué puedo ayudarte?\n\nEscribe 'ayuda' para ver los comandos disponibles."})
    
    elif session['chat_moto_paso'] == 'pedir_nombre':
        if mensaje:
            session['chat_moto_datos']['nombre'] = mensaje
            session['chat_moto_paso'] = 'pedir_documento'
            return jsonify({"respuesta": "Ahora, por favor ingresa tu número de documento de identidad:"})
        else:
            return jsonify({"respuesta": "Por favor, ingresa tu nombre completo:"})
    
    elif session['chat_moto_paso'] == 'pedir_documento':
        if mensaje:
            documento = mensaje
            db = get_db()
            cursor = db.cursor()
            
            # Verificar si el usuario existe
            cursor.execute("SELECT * FROM usuarios WHERE documento = ?", (documento,))
            usuario = cursor.fetchone()
            
            if usuario:
                # Verificar si el nombre ingresado coincide con el nombre del usuario
                if usuario['nombre'].lower() != session['chat_moto_datos']['nombre'].lower():
                    return jsonify({"respuesta": f"El documento {documento} ya está registrado a nombre de {usuario['nombre']}. Si eres tú, por favor ingresa tu nombre correctamente. Si no, por favor ingresa otro documento."})
                else:
                    session['chat_moto_usuario'] = dict(usuario)
                    session['chat_moto_paso'] = 'menu_principal'
                    return jsonify({"respuesta": f"¡Hola {usuario['nombre']}! ¿Qué deseas hacer?\n1. Agendar cita\n2. Ver citas agendadas\n3. Salir"})
            else:
                session['chat_moto_datos']['documento'] = documento
                session['chat_moto_paso'] = 'confirmar_registro'
                return jsonify({"respuesta": "No te encuentro en nuestro sistema. ¿Deseas registrarte con los datos proporcionados? (Responde 'si' o 'no')"})
        else:
            return jsonify({"respuesta": "Por favor, ingresa tu número de documento de identidad:"})
    
    elif session['chat_moto_paso'] == 'confirmar_registro':
        if mensaje in ['si', 'sí']:
            # Registrar al usuario
            db = get_db()
            cursor = db.cursor()
            cursor.execute("INSERT INTO usuarios (nombre, documento) VALUES (?, ?)", 
                          (session['chat_moto_datos']['nombre'], session['chat_moto_datos']['documento']))
            db.commit()
            
            # Obtener el usuario recién creado
            cursor.execute("SELECT * FROM usuarios WHERE documento = ?", (session['chat_moto_datos']['documento'],))
            usuario = cursor.fetchone()
            session['chat_moto_usuario'] = dict(usuario)
            session['chat_moto_paso'] = 'menu_principal'
            return jsonify({"respuesta": "¡Registro exitoso! ¿Qué deseas hacer?\n1. Agendar cita\n2. Ver citas agendadas\n3. Salir"})
        else:
            # Reiniciar
            session['chat_moto_paso'] = 'inicio'
            return jsonify({"respuesta": "Entendido. Si deseas agendar una cita, por favor proporciona tus datos nuevamente."})
    
    elif session['chat_moto_paso'] == 'menu_principal':
        if mensaje == '1' or 'agendar' in mensaje:
            session['chat_moto_paso'] = 'agendar_fecha'
            return jsonify({"respuesta": "Para agendar una cita, necesito saber la fecha. ¿Para qué día deseas agendar? (Formato: AAAA-MM-DD)"})
        elif mensaje == '2' or 'ver' in mensaje:
            # Mostrar citas del usuario
            db = get_db()
            cursor = db.cursor()
            cursor.execute("""
                SELECT c.id, c.fecha, c.hora, c.marca_moto, c.estado 
                FROM citas c 
                WHERE c.usuario_id = ? AND c.estado = 'agendada'
                ORDER BY c.fecha, c.hora
            """, (session['chat_moto_usuario']['id'],))
            citas = cursor.fetchall()
            
            if citas:
                respuesta = "Tus citas agendadas:\n"
                for cita in citas:
                    respuesta += f"ID: {cita['id']}, Fecha: {cita['fecha']}, Hora: {cita['hora']}, Moto: {cita['marca_moto']}\n"
                respuesta += "\nPara cancelar una cita, escribe 'cancelar' seguido del ID. Para posponer, escribe 'posponer' seguido del ID."
                respuesta += "\n\n1. Volver al menú"
                session['chat_moto_paso'] = 'gestionar_cita'
                return jsonify({"respuesta": respuesta})
            else:
                # Cambiamos al paso sin_citas_menu
                session['chat_moto_paso'] = 'sin_citas_menu'
                return jsonify({"respuesta": "No tienes citas agendadas. ¿Deseas agendar una nueva cita?\n1. Agendar cita\n2. Salir"})
        elif mensaje == '3' or 'salir' in mensaje:
            # Cerrar sesión
            if 'chat_moto_usuario' in session:
                session.pop('chat_moto_usuario')
            if 'chat_moto_paso' in session:
                session.pop('chat_moto_paso')
            if 'chat_moto_datos' in session:
                session.pop('chat_moto_datos')
            return jsonify({"respuesta": "Sesión cerrada. ¡Hola! Soy el asistente para agendar citas de mantenimiento de motos. ¿En qué puedo ayudarte?"})
        else:
            return jsonify({"respuesta": "Opción no reconocida. Por favor, selecciona:\n1. Agendar cita\n2. Ver citas agendadas\n3. Salir"})
    
    # Nuevo paso: manejar el menú cuando no hay citas
    elif session['chat_moto_paso'] == 'sin_citas_menu':
        if mensaje == '1' or 'agendar' in mensaje:
            session['chat_moto_paso'] = 'agendar_fecha'
            return jsonify({"respuesta": "Para agendar una cita, necesito saber la fecha. ¿Para qué día deseas agendar? (Formato: AAAA-MM-DD)"})
        elif mensaje == '2' or 'salir' in mensaje:
            # Cerrar sesión
            if 'chat_moto_usuario' in session:
                session.pop('chat_moto_usuario')
            if 'chat_moto_paso' in session:
                session.pop('chat_moto_paso')
            if 'chat_moto_datos' in session:
                session.pop('chat_moto_datos')
            return jsonify({"respuesta": "Sesión cerrada. ¡Hola! Soy el asistente para agendar citas de mantenimiento de motos. ¿En qué puedo ayudarte?"})
        else:
            return jsonify({"respuesta": "Opción no reconocida. Por favor, selecciona:\n1. Agendar cita\n2. Salir"})
    
    elif session['chat_moto_paso'] == 'agendar_fecha':
        try:
            # Validar formato de fecha
            fecha = datetime.strptime(mensaje, "%Y-%m-%d").date()
            
            # Verificar que la fecha no sea anterior a hoy
            if fecha < datetime.now().date():
                return jsonify({"respuesta": "La fecha debe ser igual o posterior a hoy. Por favor, ingresa una fecha válida (Formato: AAAA-MM-DD)"})
            
            session['chat_moto_datos']['fecha'] = mensaje
            session['chat_moto_paso'] = 'agendar_hora'
            
            # Obtener horas disponibles para esa fecha
            db = get_db()
            cursor = db.cursor()
            cursor.execute("SELECT hora FROM citas WHERE fecha = ? AND estado = 'agendada'", (mensaje,))
            horas_ocupadas = [cita['hora'] for cita in cursor.fetchall()]
            
            # Generar horas disponibles (cada 2 horas desde las 8:00 AM hasta las 6:00 PM)
            horas_disponibles = []
            for hora in range(8, 19, 2):
                hora_str = f"{hora:02d}:00"
                if hora_str not in horas_ocupadas:
                    horas_disponibles.append(hora_str)
            
            if horas_disponibles:
                respuesta = "Horas disponibles:\n" + "\n".join(horas_disponibles) + "\n\nPor favor, selecciona una hora:"
                return jsonify({"respuesta": respuesta})
            else:
                return jsonify({"respuesta": "No hay horas disponibles para esa fecha. Por favor, selecciona otra fecha."})
        except ValueError:
            return jsonify({"respuesta": "Formato de fecha inválido. Por favor, usa el formato AAAA-MM-DD."})
    
    elif session['chat_moto_paso'] == 'agendar_hora':
        hora = mensaje
        # Validar que la hora esté en el formato correcto
        try:
            datetime.strptime(hora, "%H:%M")
            hora_int = int(hora.split(':')[0])
            
            # Verificar que sea una hora válida (entre 8:00 y 18:00, y en intervalos de 2 horas)
            if hora_int < 8 or hora_int >= 18 or hora_int % 2 != 0:
                return jsonify({"respuesta": "Hora no válida. Por favor, selecciona una hora de la lista."})
            
            # Verificar que la hora esté disponible
            db = get_db()
            cursor = db.cursor()
            cursor.execute("SELECT id FROM citas WHERE fecha = ? AND hora = ? AND estado = 'agendada'", 
                         (session['chat_moto_datos']['fecha'], hora))
            if cursor.fetchone():
                return jsonify({"respuesta": "Lo siento, esa hora ya está ocupada. Por favor, selecciona otra hora."})
            
            session['chat_moto_datos']['hora'] = hora
            session['chat_moto_paso'] = 'agendar_marca'
            return jsonify({"respuesta": "¿Cuál es la marca de tu moto?"})
        except ValueError:
            return jsonify({"respuesta": "Formato de hora inválido. Por favor, usa el formato HH:MM."})
    
    elif session['chat_moto_paso'] == 'agendar_marca':
        if mensaje:
            session['chat_moto_datos']['marca_moto'] = mensaje
            
            # Guardar la cita
            db = get_db()
            cursor = db.cursor()
            cursor.execute("""
                INSERT INTO citas (usuario_id, fecha, hora, marca_moto)
                VALUES (?, ?, ?, ?)
            """, (
                session['chat_moto_usuario']['id'],
                session['chat_moto_datos']['fecha'],
                session['chat_moto_datos']['hora'],
                mensaje
            ))
            db.commit()
            
            session['chat_moto_paso'] = 'menu_principal'
            return jsonify({"respuesta": f"¡Cita agendada con éxito! Fecha: {session['chat_moto_datos']['fecha']}, Hora: {session['chat_moto_datos']['hora']}. ¿Deseas algo más?\n1. Agendar cita\n2. Ver citas agendadas\n3. Salir"})
        else:
            return jsonify({"respuesta": "Por favor, ingresa la marca de tu moto."})
    
    elif session['chat_moto_paso'] == 'gestionar_cita':
        if mensaje.startswith('cancelar'):
            try:
                cita_id = int(mensaje.split()[1])
                db = get_db()
                cursor = db.cursor()
                
                # Verificar que la cita pertenezca al usuario
                cursor.execute("SELECT * FROM citas WHERE id = ? AND usuario_id = ?", (cita_id, session['chat_moto_usuario']['id']))
                cita = cursor.fetchone()
                
                if cita:
                    cursor.execute("UPDATE citas SET estado = 'cancelada' WHERE id = ?", (cita_id,))
                    db.commit()
                    return jsonify({"respuesta": "Cita cancelada con éxito. ¿Deseas algo más?\n1. Agendar cita\n2. Ver citas agendadas\n3. Salir"})
                else:
                    return jsonify({"respuesta": "No se encontró una cita con ese ID o no te pertenece. Por favor, verifica e intenta nuevamente.\n\n1. Volver al menú"})
            except (IndexError, ValueError):
                return jsonify({"respuesta": "Por favor, indica el ID de la cita que deseas cancelar. Ejemplo: cancelar 1"})
        
        elif mensaje.startswith('posponer'):
            try:
                cita_id = int(mensaje.split()[1])
                db = get_db()
                cursor = db.cursor()
                
                # Verificar que la cita pertenezca al usuario
                cursor.execute("SELECT * FROM citas WHERE id = ? AND usuario_id = ?", (cita_id, session['chat_moto_usuario']['id']))
                cita = cursor.fetchone()
                
                if cita:
                    session['chat_moto_datos']['cita_id'] = cita_id
                    session['chat_moto_paso'] = 'posponer_fecha'
                    return jsonify({"respuesta": "Para posponer la cita, necesito la nueva fecha. ¿Para qué día? (Formato: AAAA-MM-DD)"})
                else:
                    return jsonify({"respuesta": "No se encontró una cita con ese ID o no te pertenece. Por favor, verifica e intenta nuevamente.\n\n1. Volver al menú"})
            except (IndexError, ValueError):
                return jsonify({"respuesta": "Por favor, indica el ID de la cita que deseas posponer. Ejemplo: posponer 1"})
        
        elif mensaje == '1' or 'volver' in mensaje:
            session['chat_moto_paso'] = 'menu_principal'
            return jsonify({"respuesta": "Has vuelto al menú principal. ¿Qué deseas hacer?\n1. Agendar cita\n2. Ver citas agendadas\n3. Salir"})
        
        else:
            return jsonify({"respuesta": "Opción no reconocida. Para cancelar una cita, escribe 'cancelar' seguido del ID. Para posponer, escribe 'posponer' seguido del ID.\n\n1. Volver al menú"})
    
    elif session['chat_moto_paso'] == 'posponer_fecha':
        try:
            # Validar formato de fecha
            fecha = datetime.strptime(mensaje, "%Y-%m-%d").date()
            
            # Verificar que la fecha no sea anterior a hoy
            if fecha < datetime.now().date():
                return jsonify({"respuesta": "La fecha debe ser igual o posterior a hoy. Por favor, ingresa una fecha válida (Formato: AAAA-MM-DD)"})
            
            session['chat_moto_datos']['nueva_fecha'] = mensaje
            session['chat_moto_paso'] = 'posponer_hora'
            
            # Obtener horas disponibles para esa fecha (excluyendo la cita actual que se está posponiendo)
            db = get_db()
            cursor = db.cursor()
            cursor.execute("SELECT hora FROM citas WHERE fecha = ? AND estado = 'agendada' AND id != ?", 
                         (mensaje, session['chat_moto_datos']['cita_id']))
            horas_ocupadas = [cita['hora'] for cita in cursor.fetchall()]
            
            # Generar horas disponibles (cada 2 horas desde las 8:00 AM hasta las 6:00 PM)
            horas_disponibles = []
            for hora in range(8, 19, 2):
                hora_str = f"{hora:02d}:00"
                if hora_str not in horas_ocupadas:
                    horas_disponibles.append(hora_str)
            
            if horas_disponibles:
                respuesta = "Horas disponibles:\n" + "\n".join(horas_disponibles) + "\n\nPor favor, selecciona una hora:"
                return jsonify({"respuesta": respuesta})
            else:
                return jsonify({"respuesta": "No hay horas disponibles para esa fecha. Por favor, selecciona otra fecha."})
        except ValueError:
            return jsonify({"respuesta": "Formato de fecha inválido. Por favor, usa el formato AAAA-MM-DD."})
    
    elif session['chat_moto_paso'] == 'posponer_hora':
        hora = mensaje
        try:
            datetime.strptime(hora, "%H:%M")
            hora_int = int(hora.split(':')[0])
            
            # Verificar que sea una hora válida (entre 8:00 y 18:00, y en intervalos de 2 horas)
            if hora_int < 8 or hora_int >= 18 or hora_int % 2 != 0:
                return jsonify({"respuesta": "Hora no válida. Por favor, selecciona una hora de la lista."})
            
            # Verificar que la hora esté disponible
            db = get_db()
            cursor = db.cursor()
            cursor.execute("SELECT id FROM citas WHERE fecha = ? AND hora = ? AND estado = 'agendada' AND id != ?", 
                         (session['chat_moto_datos']['nueva_fecha'], hora, session['chat_moto_datos']['cita_id']))
            if cursor.fetchone():
                return jsonify({"respuesta": "Lo siento, esa hora ya está ocupada. Por favor, seleccione otra hora."})
            
            # Actualizar la cita
            cursor.execute("""
                UPDATE citas 
                SET fecha = ?, hora = ? 
                WHERE id = ? AND usuario_id = ?
            """, (
                session['chat_moto_datos']['nueva_fecha'],
                hora,
                session['chat_moto_datos']['cita_id'],
                session['chat_moto_usuario']['id']
            ))
            db.commit()
            
            session['chat_moto_paso'] = 'menu_principal'
            return jsonify({"respuesta": f"Cita pospuesta con éxito. Nueva fecha: {session['chat_moto_datos']['nueva_fecha']}, Hora: {hora}. ¿Deseas algo más?\n1. Agendar cita\n2. Ver citas agendadas\n3. Salir"})
        except ValueError:
            return jsonify({"respuesta": "Formato de hora inválido. Por favor, usa el formato HH:MM."})
    
    else:
        return jsonify({"respuesta": "Lo siento, no entiendo tu solicitud. Por favor, intenta de nuevo o escribe 'ayuda' para ver los comandos disponibles."})






@app.route("/verificar_sesion_chat", methods=["GET"])
def verificar_sesion_chat():
    # Verificar si hay una sesión de chat activa
    if session.get('chat_moto_usuario') and session.get('chat_moto_paso') == 'menu_principal':
        return jsonify({"sesion_activa": True})
    else:
        # Limpiar la sesión si no está en el estado esperado
        if 'chat_moto_usuario' in session:
            session.pop('chat_moto_usuario')
        if 'chat_moto_paso' in session:
            session.pop('chat_moto_paso')
        if 'chat_moto_datos' in session:
            session.pop('chat_moto_datos')
        return jsonify({"sesion_activa": False})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)