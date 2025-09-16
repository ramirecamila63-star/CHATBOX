#pip install virtualenv
#python -m venv entorno1
#cd entorno1 
#.\Scripts\Activate
from flask import Flask

app = Flask(__name__)

@app.route("/")
def index():
    return "Hola Mundo"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=81, debug=True)