from django import forms
import tweepy
from django.core.exceptions import ValidationError
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from SMAapp.models import User
from django.core.urlresolvers import reverse_lazy


def get_usernames():
    options = ()
    options = list(options)
    queryset = User.objects
    for q in queryset:
        options.append((q.name, q.name))
    options = tuple(options)
    return options


class SearchUserForm(forms.Form):

    username_input = forms.ChoiceField(choices=get_usernames(), label='')

    helper = FormHelper()
    helper.form_class = 'form-horizontal'
    helper.form_action = reverse_lazy('smaapp:search_redirect')     # redirects to an intermediate view
    helper.label_class = 'col-sm-2'
    helper.field_class = 'col-sm-12'
    helper.layout = Layout()
    helper.add_input(Submit('search', 'Search'))


class CompareUsersForm(forms.Form):

    first_username = forms.ChoiceField(choices=get_usernames(), label='')
    second_username = forms.ChoiceField(choices=get_usernames(), label='')

    helper = FormHelper()
    helper.form_class = 'form-horizontal'
    helper.form_action = reverse_lazy('smaapp:compare_redirect')
    helper.label_class = 'col-sm-2'
    helper.field_class = 'col-sm-12'
    helper.layout = Layout()
    helper.add_input(Submit('compare', 'Compare'))



