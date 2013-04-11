from flask import Flask
app = Flask(__name__)

@app.route('/')
def index():
    return "Grupo de Desenvolvedores Python de Goiás"

if __name__ == '__main__':
    app.run()