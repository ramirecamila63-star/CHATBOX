#pip install virtualenv
#python -m venv entorno1
#cd entorno1 
#.\Scripts\Activate

#cd chatbot
#source ./entorno1/bin/activate
#python main.py
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route("/home")
def home():
    return "Hola mundo"

@app.route("/index")
def index():
    return render_template('index.html')

@app.route("/base")
def base():
    return render_template('base.html')

@app.route('/mision')
def mision():
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

@app.route("/programas", methods=['GET', 'POST'])
def programas():
    if request.method == 'GET':
        return render_template('programas.html')
    else:
        codigo = request.form.get('codigo')
        descripcion = request.form.get('descripcion')
        
        #print("="*50)
        print("DATOS RECIBIDOS EN PROGRAMAS:")
        print(f"Código del programa: {codigo}")
        print(f"Descripción del programa: {descripcion}")
        #print("="*50)
        
        return render_template('vision.html', 
                              codigo=codigo, 
                              descripcion=descripcion,
                              from_form=True)

app.run(host='0.0.0.0', port=5000, debug=True)