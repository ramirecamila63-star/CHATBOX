#pip install virtualenv
#python -m venv entorno1
#cd entorno1 
#.\Scripts\Activate

#cd chatbot
#source ./entorno1/bin/activate
#python main.py
from flask import Flask, render_template

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

@app.route("/vision")
def vision():
    return render_template('vision.html')

@app.route("/programas")
def programas():
    return render_template('programas.html')

app.run(host='0.0.0.0', port=5000, debug=True)