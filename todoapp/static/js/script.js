// cacheando seletores jQuery
let $tarefas = $('#tarefas')
let $listas = $('#listas')
let $modal = $('#modal-confirmacao')
let $modal_compartilhar_lista = $('#modal-compartilhar-lista')
let $lista_ativa = $('#lista')
let $lista_ctx_menu;
let $progresso_lista_ativa = $lista_ativa.find('#progresso')
let $ctx_menu = $('.context-menu')

let qtd_concluidas;
let qtd_tarefas;
let id_lista_ativa;
let emails;

$.ajax({
    type: 'GET',
    url: '/api/emails',
    complete: function(response) {
        emails = response['responseJSON']
    }
})

$.ajax({
    type: 'GET',
    url: '/api/listas',
    complete: function(response){
        const queryString = window.location.search;
        const urlParams = new URLSearchParams(queryString);
        const id_lista = urlParams.get('id_lista');

        let json = response['responseJSON'];
        for (let i = 0; i < json.length; i++) {
            let nova_lista = document.createElement('button');
            nova_lista.id = "lista_" + json[i]['id']
            nova_lista.className= 'list-group-item list-group-item-action';
            if (i === 0) {
                nova_lista.className= 'list-group-item list-group-item-action active';
            }
            nova_lista.innerText = json[i]['nome'];
            nova_lista.style.border = 'none';
            $listas.append(nova_lista);
            if (i === 0 && id_lista == null) {
                nova_lista.click();
            }
            else if (id_lista === `${json[i]['id']}`) {
                nova_lista.click();
            }
        }
    }
})

$('#criar_lista').on('click', function(){
    $.ajax({
        type: 'POST',
        url: '/api/listas',
        complete: function(msg){
            let lista = msg["responseJSON"]
            let nova_lista = document.createElement('button');
            nova_lista.className= 'list-group-item list-group-item-action';
            nova_lista.innerText = lista["nome"];
            nova_lista.style.border = 'none';
            nova_lista.id = 'lista_' + lista['id'];
            $listas.append(nova_lista);
            nova_lista.click();
            tata.success('Sucesso', 'Lista criada com sucesso', {
                position: 'br',
                duration: 2000
            })
        }
    })
});

$('#excluir_lista').on('click', function () {
    $modal.find('.modal-title').text('Excluir lista')
    $modal.find('.modal-body').text('Tem certeza que deseja excluir essa lista?')
    $modal.modal('show')
    let $modalfooter = $modal.find('.modal-footer')
    $modalfooter.off()
    $modalfooter.on('click', '#confirmar', function() {
        $.ajax({
            type: 'DELETE',
            url: '/api/listas/' + id_lista_ativa,
            complete: function(){
                $listas.find('.active').remove()

                let $listasbutton = $listas.find('button')

                if ($listasbutton.length > 0) {
                    $listasbutton.first().click()
                }
                else {
                    $tarefas.children().not(':first').remove()

                    let $nome_lista = $lista_ativa.find('#nome_lista')
                    $nome_lista.text('Selecione ou crie uma lista!')
                    $nome_lista.attr('contenteditable', 'false')

                    $lista_ativa.find('#descricao_lista').text('')
                    $lista_ativa.find('#botoes_lista').addClass('invisible')
                    $lista_ativa.find('.progress').addClass('invisible')
                }

                tata.success('Sucesso', 'Lista excluída com sucesso', {
                    position: 'br',
                    duration: 2000
                })
            }
        })
    })
})

$('#editar_lista').on('click', function () {
    let id_lista = $listas.find('.active').attr('id').split('_')[1];
    let nome_lista = $('#nome_lista').text()
    let descricao_lista = $('#descricao_lista').text()
    $(`#lista_${id_lista}`).text(nome_lista)

    $.ajax({
        type: 'PATCH',
        url: `api/listas/${id_lista}`,
        dataType: "json",
        contentType: "application/json",
        data: JSON.stringify(
            {
                'nome': nome_lista,
                'descricao': descricao_lista
            }
        ),
        success: function () {
            tata.success('Sucesso', 'Lista atualizada com sucesso', {
                position: 'br',
                duration: 2000
            })
        }
    })
})

$listas.on('click', 'button', function() {
    $(this).addClass('active').siblings().removeClass('active');
    id_lista_ativa = $(this).attr('id').split('_')[1];
    $.ajax({
        type: 'GET',
        url: '/api/listas/' + id_lista_ativa,
        complete: function(msg){
            // alterando nome
            let $nome_lista = $lista_ativa.find('#nome_lista')
            $nome_lista.text(msg["responseJSON"]['nome'])
            $nome_lista.attr('contenteditable', 'true')

            // alterando descrição
            let $descricao_lista = $lista_ativa.find('#descricao_lista')
            $descricao_lista.text(msg["responseJSON"]['descricao'])
            $descricao_lista.attr('contenteditable', 'true')

            // mostrando botões e barra de progresso
            $lista_ativa.find('#botoes_lista').removeClass('invisible')
            $lista_ativa.find('.progress').removeClass('invisible')

            // removendo da tela as tarefas da lista antiga, exceto a primeira,
            // que serve de modelo para desenhar tarefas
            $tarefas.children().not(':first').remove()

            let lista = msg["responseJSON"];
            let tarefas = lista['tarefas'];
            qtd_concluidas = 0;
            qtd_tarefas = 0;
            if (tarefas) {
                tarefas.sort(function(a, b) {
                    let data1 = `${a['data']}`.split('/');
                    data1 = parseInt(`${data1[2]}${data1[1]}${data1[0]}`);
                    let data2 = `${b['data']}`.split('/');
                    data2 = parseInt(`${data2[2]}${data2[1]}${data2[0]}`);
                    return a['concluida'] - b['concluida'] || data1 - data2;
                })
                for (let i = 0; i < tarefas.length; i++) {
                    desenharTarefa(tarefas[i]);
                    if (tarefas[i]['concluida'] === true) {
                        qtd_concluidas++;
                    }
                    qtd_tarefas++;
                }
            }
            let porcentagem = '0%'
            if (qtd_tarefas !== 0) {
                porcentagem = `${qtd_concluidas*100 / qtd_tarefas}%`
            }
            $progresso_lista_ativa.css('width', porcentagem)
        }
    })
})

$listas.on('contextmenu', 'button', function (event) {
    $lista_ctx_menu = $(this)
    $ctx_menu.empty()
    event.preventDefault()
    $ctx_menu.append('<li>Enviar cópia</li>')
    $ctx_menu.finish().toggle(100)
    $ctx_menu.css({
        top: event.pageY + 'px',
        left: event.pageX + 'px'
    })
})

$(document).bind("mousedown", function (event) {
    if ($(event.target).parents(".context-menu").length === 0) {
        $ctx_menu.hide(100)
    }
    if ($(event.target).closest('#modal-compartilhar-lista').length === 0) {
        let $email = $modal_compartilhar_lista.find('#email-autocomplete')
        $email.removeClass('is-invalid')
        $modal_compartilhar_lista.find('.invalid-feedback').remove()
    }
});

function enviarCopiaLista() {
    $modal_compartilhar_lista.find('.modal-title').text("Enviar cópia de '" + $lista_ctx_menu.text() + "'")
    $modal_compartilhar_lista.modal('show')
    autocomplete(document.getElementById('email-autocomplete'), emails)
    let $modalfooter = $modal_compartilhar_lista.find('.modal-footer')
    $modalfooter.off()

    $modalfooter.on('click', '#confirmar', function() {
        let id_lista = $lista_ctx_menu.attr('id').split('_')[1]
        let $email = $modal_compartilhar_lista.find('#email-autocomplete')

        function validateEmail(email) {
            const re = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
            return re.test(email);
        }

        if (!validateEmail($email.val())) {
            $email.addClass('is-invalid')
            $modal_compartilhar_lista.find('.invalid-feedback').remove()
            $email.parent().append('<div class="invalid-feedback"><span>Email inválido</span></div>')
        }

        else {
            $modal_compartilhar_lista.modal('hide')
            $.ajax({
                type: 'POST',
                url: `/api/listas/enviar_copia`,
                dataType: "json",
                contentType: "application/json",
                data: JSON.stringify(
                    {
                        'id_lista': id_lista,
                        'email_recebedor': $email.val()
                    }
                ),
            })
        }
    })
}

$ctx_menu.click('li', function(){
    switch($(this).text()) {
        case "Enviar cópia":
            enviarCopiaLista()
            break
    }

    $ctx_menu.hide(100);
});

$('#criar_tarefa').on('click', function () {
    $.ajax({
        type: 'POST',
        url: '/api/listas/' + id_lista_ativa + '/tarefas',
        complete: function(msg){
            desenharTarefa(msg["responseJSON"])
            qtd_tarefas++;

            let porcentagem = qtd_concluidas * 100 / qtd_tarefas;
            $progresso_lista_ativa.css('width', porcentagem.toString() + '%')

            tata.success('Sucesso', 'Tarefa criada com sucesso', {
                position: 'br',
                duration: 2000
            })
        }
    })
})

$tarefas.on('click', 'input', function(){
    let id_tarefa = $(this).attr('id')
    let checkedValue = $(this).is(':checked');

    $.ajax({
        type: 'PATCH',
        url: `api/listas/${id_lista_ativa}/tarefas/${id_tarefa}`,
        dataType: "json",
        contentType: "application/json",
        data: JSON.stringify(
            {
                'concluida': checkedValue
            }
        ),
        complete: function(){

            if (checkedValue === true) {
                qtd_concluidas++;
            } else {
                qtd_concluidas--;
            }
            let porcentagem = (qtd_concluidas * 100 / qtd_tarefas).toString() + '%'
            $progresso_lista_ativa.css('width', porcentagem)

            tata.success('Sucesso', 'Tarefa atualizada com sucesso', {
                position: 'br',
                duration: 2000
            })
        }
    })
})

$tarefas.on('click', '.excluir-tarefa', function () {
    let id_tarefa = $(this).attr('id')

    $modal.find('.modal-title').text('Excluir tarefa')
    $modal.find('.modal-body').text('Tem certeza que deseja excluir essa tarefa?')
    $modal.modal('show')
    let $modalfooter = $modal.find('.modal-footer')
    $modalfooter.off()
    $modalfooter.on('click', '#confirmar', function () {
        $.ajax({
            type: 'DELETE',
            url: `api/listas/${id_lista_ativa}/tarefas/${id_tarefa}`,
            complete: function () {
                qtd_tarefas--;
                let checkedValue = $('#tarefa_'+id_tarefa).find('input, #'+id_tarefa).is(':checked')
                if (checkedValue === true) {
                    qtd_concluidas--;
                }

                let porcentagem = 0;
                if (qtd_tarefas !== 0) {
                    porcentagem = qtd_concluidas * 100 / qtd_tarefas
                }

                $progresso_lista_ativa.css('width', porcentagem.toString() + '%')
                let id_tarefa_conluida = `tarefa_${id_tarefa}`
                $tarefas.find('#' + id_tarefa_conluida).remove()

                tata.success('Sucesso', 'Tarefa excluída com sucesso', {
                    position: 'br',
                    duration: 2000
                })
            }
        })
    });
})

$tarefas.on('click', '.editar-tarefa', function () {
    let id_tarefa = $(this).attr('id')
    let $tarefa = $('#tarefa_'+id_tarefa)

    let titulo_tarefa = $tarefa.find('#titulo_tarefa').text()
    let descricao_tarefa = $tarefa.find('#descricao_tarefa').text()

    $.ajax({
        type: 'PATCH',
        url: `api/listas/${id_lista_ativa}/tarefas/${id_tarefa}`,
        dataType: "json",
        contentType: "application/json",
        data: JSON.stringify(
            {
                'titulo': titulo_tarefa,
                'descricao': descricao_tarefa
            }
        ),
        success: function () {
            tata.success('Sucesso', 'Tarefa atualizada com sucesso', {
                position: 'br',
                duration: 2000
            })
        }
    })
})

function desenharTarefa(tarefa) {
    let $tarefa_model = $('#model_tarefa').clone().css('display', '')
    $tarefa_model.find('#_titulo_tarefa').text(tarefa["titulo"]).attr('id', 'titulo_tarefa')
    $tarefa_model.find('#_descricao_tarefa').text(tarefa["descricao"]).attr('id', 'descricao_tarefa')
    $tarefa_model.find('#concluido_tarefa').prop('checked', tarefa['concluida'] ? 'true' : '').attr('id', tarefa['id'].toString())
    $tarefa_model.find('.excluir-tarefa').attr('id', tarefa['id'].toString())
    $tarefa_model.find('.editar-tarefa').attr('id', tarefa['id'].toString())

    $tarefa_model.attr('id', `tarefa_${tarefa['id']}`)
    $tarefas.append($tarefa_model)
}

function filterList() {
    let input = document.getElementById('busca');
    let filter = input.value.toUpperCase();
    if (filter.startsWith(':')) {
        filter = filter.substring(1, filter.length)
        let tarefas, tarefa, titulo;
        tarefas = document.getElementById("tarefas").getElementsByClassName("col");
        for (let i = 0; i < tarefas.length; i++) {
            tarefa = tarefas[i];
            titulo = tarefa.getElementsByClassName("text-left")[0].textContent;

            if (titulo.includes('\\\\modelo')) {
                continue
            }

            let filters = filter.split(" ");
            filters = filters.filter(f => f.length)

            let shouldDisplay = true
            filters.forEach(filt => {
                shouldDisplay = shouldDisplay && titulo.toUpperCase().includes(filt)
            })

            tarefas[i].style.display = (shouldDisplay || filters.length === 0) ? "" : "none";
        }
    }
    else {
        let ul, li, a, i, txtValue;
        ul = document.getElementById("listas");
        li = ul.getElementsByClassName("list-group-item");

        for (i = 0; i < li.length; i++) {
            a = li[i];
            txtValue = a.textContent || a.innerText;

            let filters = filter.split(" ")
            filters = filters.filter(f => f.length)

            let shouldDisplay = true

            filters.forEach(filt => {
                shouldDisplay = shouldDisplay && txtValue.toUpperCase().includes(filt)
            })

            li[i].style.display = (shouldDisplay || filters.length === 0) ? "" : "none";
        }
    }
}