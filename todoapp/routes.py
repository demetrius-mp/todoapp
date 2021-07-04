from flask import render_template, url_for, flash, redirect
from todoapp.forms import FormCadastro, FormLogin
from flask_login import login_user, current_user, logout_user, login_required
from todoapp.models import Usuario
from todoapp import app, bcrypt


@app.route('/')
@app.route('/home')
def sobre():
    return render_template('home.html', title='Sobre')


@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if current_user.is_authenticated:
        return redirect(url_for('listas'))
    form = FormCadastro()
    if form.validate_on_submit():
        hash_senha = bcrypt.generate_password_hash(form.senha.data).decode('utf-8')
        Usuario.create(nome=form.nome.data, email=form.email.data, senha=hash_senha)
        flash(f'Usuário {form.nome.data} foi criado com sucesso!', 'success')
        return redirect(url_for('login'))

    return render_template('cadastro.html', title='Cadastro', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('listas'))
    form = FormLogin()
    if form.validate_on_submit():
        user = Usuario.get_or_none(Usuario.email == form.email.data)
        if user and bcrypt.check_password_hash(user.senha, form.senha.data):
            login_user(user)
            return redirect(url_for('listas'))
        else:
            flash('Falha no login. Verifique o email e senha inseridos.', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('sobre'))


@app.route('/listas')
@login_required
def listas():
    return render_template('listas.html', title='Listas')


@app.errorhandler(404)
def error_404(e):
    flash('Página não encontrada', 'danger')
    return redirect(url_for('listas'))
