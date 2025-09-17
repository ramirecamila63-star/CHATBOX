#pip install virtualenv
#python -m venv entorno1
#cd entorno1 
#.\Scripts\Activate
from flask import Flask, render_template

app = Flask(__name__)

@app.route("/home")
def home():
    return "Hola mundo"

@app.route("/index")
def index():
    return render_template('index.html')


app.run(host='0.0.0.0', port=5000, debug=True)