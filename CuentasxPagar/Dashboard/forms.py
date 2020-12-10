from django import forms

class FormCreateUser(forms.Form):
    RFC = forms.CharField(widget=forms.TextInput(
        attrs={
        'class':'form-control',
        'placeholder':'RFC',
        'size':60,
        'id': 'RFC',
        'autocomplete': 'off',
        'disabled':'disabled'
    }
    ))

class FormEliminarEvidencias(forms.Form):
    Viaje = forms.CharField(widget=forms.TextInput(
        attrs={
        'class':'form-control',
        'placeholder':'Buscar...',
        'id': 'SearchEvidenciaToDelete',
        'autocomplete': 'off'
    }
    ))
