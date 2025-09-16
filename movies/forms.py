from django import forms
from .models import MovieRequest

class MovieRequestForm(forms.ModelForm):
    class Meta:
        model = MovieRequest
        fields = ['movie_name', 'description']
        widgets = {
            'movie_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter movie name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter movie description',
                'rows': 4
            })
        }
        labels = {
            'movie_name': 'Movie Name',
            'description': 'Description'
        }
