from peewee import JOIN, DoesNotExist, chunked
from playhouse.shortcuts import model_to_dict
from todoapp.models import Usuario, Lista, Tarefa, NotificacaoCopiaLista
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


@app.route('/api/listas/copias', methods=['POST', 'PATCH'])
@login_required
def api_enviar_copia():
    if request.method == 'POST':
        data = request.json

        id_lista = int(data['id_lista'])
        lista = Lista.get_or_none(Lista.id == id_lista)
        if not lista:
            return jsonify({'msg': 'Lista não encontrada'})

        email_recebedor = data['email_recebedor']
        recebido_por = Usuario.get_or_none(Usuario.email == email_recebedor)
        if not recebido_por:
            return jsonify({'msg': 'Usuário não encontrado'})

        texto = f'Cópia de lista de {current_user.nome}'
        notificacao = NotificacaoCopiaLista.create(texto=texto, lista=lista, enviado_por=current_user.id,
                                                   recebido_por=recebido_por)

        '''
        copia_lista = Lista.create(nome=lista.nome, descricao=lista.descricao)
        
        tarefas = [{
            'titulo': tarefa.titulo,
            'descricao': tarefa.descricao,
            'lista': copia_lista
        } for tarefa in lista.tarefas]

        with db.atomic():
            for batch in chunked(tarefas, 100):
                Tarefa.insert_many(batch).execute()

        return jsonify({'msg': 'success'})
        '''
        return jsonify({'msg': 'success'})

    if request.method == 'PATCH':
        action = request.args.get('action')
        data = request.json

        ntf = NotificacaoCopiaLista.get_or_none(NotificacaoCopiaLista.id == data['id_ntf'])
        if not ntf:
            return jsonify({'msg': 'fail'})

        if action == 'aceitar':
            lista = Lista.get_or_none(Lista.id == ntf.lista)

            copia_lista = Lista.create(nome=lista.nome, descricao=lista.descricao, usuario=current_user.id)

            tarefas = [{
                'titulo': tarefa.titulo,
                'descricao': tarefa.descricao,
                'lista': copia_lista
            } for tarefa in lista.tarefas]

            with db.atomic():
                for batch in chunked(tarefas, 100):
                    Tarefa.insert_many(batch).execute()

            return jsonify(model_to_dict(copia_lista, recurse=False))

        return jsonify({'msg': 'fail'})


@app.route('/api/notificacoes', methods=['GET'])
@login_required
def api_notificacoes():
    if request.method == 'GET':
        notificacoes = (NotificacaoCopiaLista
                        .select(NotificacaoCopiaLista.id,
                                NotificacaoCopiaLista.texto,
                                Lista.nome,
                                Usuario.nome
                                )
                        .join(Lista).join(Usuario)
                        .where(NotificacaoCopiaLista.recebido_por == current_user.id))

        notificacoes = [{
            'id': n.id,
            'texto': n.texto,
            'lista': n.lista.nome,
            'enviado_por': n.lista.usuario.nome
        } for n in notificacoes]
        return jsonify(notificacoes)
