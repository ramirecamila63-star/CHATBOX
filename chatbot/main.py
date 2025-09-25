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
            cursor.execute("INSERT INTO carrera (descripcion) VALUES (?)", (descripcion,))
            db.commit()

            last_id = cursor.lastrowid
            print(f"Programa guardado: ID {last_id}, Descripción: {descripcion}")
            
            return redirect(url_for('respuesta', id=last_id, descripcion=descripcion))
        except sqlite3.IntegrityError as e:
            print(f"Error: {e}")
          
            return render_template('mision.html', error="La descripción del programa ya existe")
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
   
    id_carrera = request.args.get('id')
    descripcion = request.args.get('descripcion')
    
    return render_template('respuesta.html', id=id_carrera, descripcion=descripcion)

@app.route("/editar_carrera/<int:id>", methods=['GET', 'POST'])
def editar_carrera(id):
    db = get_db()
    cursor = db.cursor()
    
    if request.method == 'POST':
        descripcion = request.form.get('descripcion')
        try:
            cursor.execute("UPDATE carrera SET descripcion = ? WHERE id = ?", (descripcion, id))
            db.commit()
            print(f"Programa actualizado: ID {id}, Nueva descripción: {descripcion}")
            return redirect(url_for('lista_carreras'))
        except Exception as e:
            print(f"Error al actualizar: {e}")
            return render_template('editar_carrera.html', id=id, error="Error al actualizar el programa")
    else:
        cursor.execute("SELECT * FROM carrera WHERE id = ?", (id,))
        programa = cursor.fetchone()
        return render_template('editar_carrera.html', programa=programa)

@app.route("/eliminar_carrera/<int:id>")
def eliminar_carrera(id):
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM carrera WHERE id = ?", (id,))
        db.commit()
        print(f"Programa eliminado: ID {id}")
    except Exception as e:
        print(f"Error al eliminar: {e}")
    return redirect(url_for('lista_carreras'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)