from peewee import JOIN, DoesNotExist, chunked
from playhouse.shortcuts import model_to_dict
from todoapp.models import Usuario, Lista, Tarefa, Notificacao
from flask import request, jsonify
from todoapp import app, db
from flask_login import current_user, login_required


@app.route('/api/listas', defaults={'id_lista': None}, methods=['GET', 'POST'])
@app.route('/api/listas/<int:id_lista>', methods=['GET', 'PATCH', 'DELETE'])
@login_required
def api_listas(id_lista):
    if request.method == 'GET':
        if id_lista:
            try:
                lista = Lista.select(Lista, Tarefa).join(Tarefa, JOIN.LEFT_OUTER).where(Lista.id == id_lista).get()
            except DoesNotExist:
                lista = None

            if not lista or lista.usuario.id != current_user.id:
                return jsonify({'msg': 'Recurso não encontrado'})

            model = model_to_dict(lista, recurse=False)
            tarefas = []
            for tarefa in lista.tarefas:
                tarefa_dict = model_to_dict(tarefa, recurse=False)
                tarefas.append(tarefa_dict)
            model.update({'tarefas': tarefas})

            return jsonify(model)

        listas = Lista.select(Lista.id, Lista.nome).where(Lista.usuario == current_user.id)
        listas = [model_to_dict(lista, recurse=False, fields_from_query=listas) for lista in listas]
        return jsonify(listas)

    elif request.method == 'POST':
        lista = Lista.create(nome='Lista de tarefas', descricao='Descrição da lista de tarefas.',
                             usuario=current_user.id)
        return jsonify(model_to_dict(lista, recurse=False))

    elif request.method == 'PATCH':
        if id_lista:
            lista = Lista.get_or_none(Lista.id == id_lista)
            if not lista or lista.usuario.id != current_user.id:
                return jsonify({'msg': 'Recurso não encontrado'})

            data = request.json
            lista.nome = data['nome']
            lista.descricao = data['descricao']
            lista.save()
            return jsonify(model_to_dict(lista, recurse=False))

        return jsonify({'msg': 'Forneça o id da lista'})

    elif request.method == 'DELETE':
        if id_lista:
            lista = Lista.get_or_none(Lista.id == id_lista)
            if not lista or lista.usuario.id != current_user.id:
                return jsonify({'msg': 'Recurso não encontrado'})

            Tarefa.delete().where(Tarefa.lista == id_lista).execute()
            lista.delete_instance()
            return jsonify({'msg': 'Recurso excluído com sucesso'})

        return jsonify({'msg': 'Forneça o id da lista'})


@app.route('/api/listas/<int:id_lista>/tarefas', defaults={'id_tarefa': None}, methods=['POST'])
@app.route('/api/listas/<int:id_lista>/tarefas/<int:id_tarefa>', methods=['GET', 'PATCH', 'DELETE'])
@login_required
def api_tarefas(id_lista, id_tarefa):
    if request.method == 'GET':
        if not id_tarefa:
            return jsonify({'msg': 'Forneça o id da tarefa'})

        tarefa = Tarefa.get_or_none(Tarefa.id == id_tarefa)
        if not tarefa or tarefa.lista.usuario.id != current_user.id:
            return jsonify({'msg': 'Recurso não encontrado'})

        return jsonify(model_to_dict(tarefa, recurse=False))

    elif request.method == 'POST':
        data = request.json
        tarefa = Tarefa.create(titulo='Tarefa', descricao='Descrição da tarefa.', lista=id_lista)
        model = model_to_dict(tarefa, recurse=False)
        return jsonify(model)

    elif request.method == 'PATCH':
        if not id_tarefa:
            return jsonify({'msg': 'Forneça o id da tarefa'})

        data = request.json
        tarefa = Tarefa.get_or_none(Tarefa.id == id_tarefa)
        if not tarefa or tarefa.lista.usuario.id != current_user.id:
            return jsonify({'msg': 'Recurso não encontrado'})

        if 'concluida' in data:
            tarefa.concluida = data['concluida']

        if 'titulo' in data:
            tarefa.titulo = data['titulo']

        if 'descricao' in data:
            tarefa.descricao = data['descricao']

        tarefa.save()

        return jsonify(model_to_dict(tarefa, recurse=False))

    elif request.method == 'DELETE':
        if not id_tarefa:
            return jsonify({'msg': 'Forneça o id da tarefa'})

        tarefa = Tarefa.get_or_none(Tarefa.id == id_tarefa)
        if not tarefa or tarefa.lista.usuario.id != current_user.id:
            return jsonify({'msg': 'Recurso não encontrado'})

        tarefa.delete_instance()
        return jsonify({'msg': 'Recurso excluído com sucesso'})


@app.route('/api/emails')
@login_required
def api_emails():
    usuarios_email = Usuario.select(Usuario.email)
    emails = [usuario.email for usuario in usuarios_email if usuario.email != current_user.email]
    return jsonify(emails)


@app.route('/api/listas/enviar_copia', methods=['POST'])
@login_required
def api_enviar_copia():
    if request.method == 'POST':
        data = request.json

        id_lista = int(data['id_lista'])
        lista = Lista.get_or_none(Lista.id == id_lista)
        if not lista:
            return jsonify({'msg': 'Lista não encontrada'})

        email_recebedor = data['email_recebedor']
        recebedor = Usuario.get_or_none(Usuario.email == email_recebedor)
        if not recebedor:
            return jsonify({'msg': 'Usuário não encontrado'})

        copia_lista = Lista.create(nome=lista.nome, descricao=lista.descricao, usuario=recebedor)

        tarefas = [{
            'titulo': tarefa.titulo,
            'descricao': tarefa.descricao,
            'lista': copia_lista
        } for tarefa in lista.tarefas]

        with db.atomic():
            for batch in chunked(tarefas, 100):
                Tarefa.insert_many(batch).execute()

        return jsonify({'msg': 'success'})


@app.route('/api/notificacoes', methods=['GET', 'POST'])
@login_required
def api_notificacoes():
    if request.method == 'GET':
        for n in current_user.notificacoes:
            print(n.texto)
        return jsonify({'msg': 'success'})

    if request.method == 'POST':
        tipo = request.args.get('tipo')
        data = request.json

        email_recebedor = data['para']
        recebedor = Usuario.get_or_none(Usuario.email == email_recebedor)
        if not recebedor:
            return jsonify({'msg': 'Usuário não encontrado'})

        texto = f'{current_user.nome} deseja enviar uma lista para você!'
        Notificacao.create(texto=texto, usuario=recebedor)
        return jsonify({'msg': 'success'})
