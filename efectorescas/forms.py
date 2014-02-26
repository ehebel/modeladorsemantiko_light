from django import forms

class SearchForm(forms.Form):
    query = forms.CharField(
        label='',
        widget=forms.TextInput(attrs={'size':32})
    )

__author__ = 'ehebel'
