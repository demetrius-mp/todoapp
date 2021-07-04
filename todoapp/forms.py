from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from todoapp.models import Usuario


class FormCadastro(FlaskForm):
    nome = StringField('Nome', validators=[DataRequired()])
    email = StringField('Email',
                        validators=[DataRequired(), Email(message='Email inválido')])
    senha = PasswordField('Senha', validators=[DataRequired()])
    confirma_senha = PasswordField('Confirma senha', validators=[DataRequired(), EqualTo('senha', message='Este campo '
                                                                                                          'deve ser '
                                                                                                          'igual à '
                                                                                                          'senha')])
    submit = SubmitField('Cadastrar')

    def validate_email(self, email):
        usuario = Usuario.get_or_none(Usuario.email == email.data)
        if usuario:
            raise ValidationError('Email já cadastrado. Por favor, utilize outro.')


class FormLogin(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(message='Email inválido')])
    senha = PasswordField('Senha', validators=[DataRequired()])
    submit = SubmitField('Login')
