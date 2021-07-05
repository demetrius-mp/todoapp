from peewee import *
from todoapp import login_manager
from flask_login import UserMixin

db = SqliteDatabase('todoapp/app.db')


@login_manager.user_loader
def load_user(id_usuario):
    return Usuario.get_or_none(Usuario.id == int(id_usuario))


class BaseModel(Model):
    class Meta:
        database = db


class Usuario(BaseModel, UserMixin):
    id = AutoField()
    nome = CharField()
    email = CharField(unique=True)
    senha = CharField()


class Lista(BaseModel):
    id = AutoField()
    nome = CharField()
    descricao = TextField()
    usuario = ForeignKeyField(Usuario, backref='listas')


class Tarefa(BaseModel):
    id = AutoField()
    titulo = CharField()
    descricao = TextField()
    concluida = BooleanField(default=False)
    lista = ForeignKeyField(Lista, backref='tarefas')


class Notificacao(BaseModel):
    id = AutoField()
    tipo = CharField(choices=['Compartilhar lista'])
    id_recurso = IntegerField()
    texto = CharField()
    usuario = ForeignKeyField(Usuario, backref='notificacoes')
