from flask import Flask
from flask_login import LoginManager
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
login_manager = LoginManager(app)
bcrypt = Bcrypt(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
login_manager.login_message = 'Faça login antes de acessar esta página.'


def create_tables():
    from todoapp.models import db, Usuario, Lista, Tarefa
    db.create_tables([Usuario, Lista, Tarefa])


from todoapp import routes
from todoapp import api
