#pip install virtualenv
#python -m venv entorno1
#cd chatbot
#cd entorno1 
#.\Scripts\Activate

#cd chatbot
#source ./entorno1/bin/activate
#python main.py

from flask import Flask, render_template, request, redirect, url_for, g
import sqlite3

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_aqui'  

DATABASE = 'base.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

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
            # Insertar usando codigo y descripcion
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

@app.route("/predict", methods=['GET', 'POST'])
def predict():
    if request.method == "POST":
        return render_template('chat.html')
    else:
        return render_template('chat.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)