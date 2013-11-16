# encoding: utf-8
from django import forms

class LoginForm(forms.Form):
    """Classe de login, apenas com usuário e senha"""
    username = forms.CharField(label=u'Usuário')
    password = forms.CharField(label=u'Senha', widget=forms.PasswordInput)
