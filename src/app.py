from flask import Flask, render_template
from dotenv import load_dotenv
import os

from config.mongodb import mongo
from Rutas.usuario import usuario
from Rutas.restaurante import restaurante
from Rutas.menu import menu
from Rutas.pedidos import pedidos
from Rutas.reseñas import reseñas

app = Flask(__name__)
load_dotenv()
app.config['MONGO_URI'] = os.getenv('MONGO_URI')
mongo.init_app(app)


@app.route('/')
def index():
    return render_template('index.html')

app.register_blueprint(usuario, url_prefix='/api')
app.register_blueprint(restaurante, url_prefix='/restaurante')
app.register_blueprint(menu, url_prefix='/menu')
app.register_blueprint(pedidos, url_prefix='/pedidos')
app.register_blueprint(reseñas, url_prefix='/reseñas')

if __name__ == "__main__":
    app.run(debug=True)