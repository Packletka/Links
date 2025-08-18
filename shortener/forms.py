from django import forms
from django.core.validators import URLValidator

class URLShortenForm(forms.Form):
    original_url = forms.CharField(
        label='Длинная ссылка',
        validators=[URLValidator()],
        widget=forms.TextInput(attrs={
            'placeholder': 'https://example.com/very-long-url...',
            'class': 'form-control'
        })
    )