from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from .models import Post

User = get_user_model()

class UserRegistration(forms.ModelForm):
    email = forms.EmailField(label='Indirizzo Email')
    #emailConfirmation = forms.EmailField(label='Conferma Email')
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'password'
        ]

class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ('title', 'text',)

    def clean_title(self):
        data = self.cleaned_data['title']
        if 'hack' in data:
            raise ValidationError('Errore: Il titolo non può contenere la parola \'hack\'')

        return data

    def clean_text(self):
        data = self.cleaned_data['text']
        if 'hack' in data:
            raise ValidationError('Errore: Il testo non può contenere la parola \'hack\'')

        return data
