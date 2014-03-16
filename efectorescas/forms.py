from django import forms

class SearchForm(forms.Form):
    query = forms.CharField(
        label='',
        widget=forms.TextInput(attrs={'size':60})
    )

__author__ = 'ehebel'