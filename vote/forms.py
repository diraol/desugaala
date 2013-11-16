# -*- coding: utf-8 -*-
"""Default Django Form file.

This one is used just for Login Form at this moment.

"""

# encoding: utf-8
from django import forms


class LoginForm(forms.Form):

    u"""Classe de login, apenas com usuário e senha."""

    username = forms.CharField(label=u'Usuário')
    password = forms.CharField(label=u'Senha', widget=forms.PasswordInput)
