from django.contrib.auth.forms import UserCreationForm
from django.forms import CharField, EmailField
from django.forms import ModelForm, Textarea, TextInput, NumberInput
from .models import Book, User


class SignUpForm(UserCreationForm):
    first_name = CharField(max_length=30, required=False)
    last_name = CharField(max_length=150, required=False)
    email = EmailField(required=False)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)

        if not self.cleaned_data['first_name']:
            user.first_name = ''
        else:
            user.first_name = self.cleaned_data['first_name']

        if not self.cleaned_data['last_name']:
            user.last_name = ''
        else:
            user.last_name = self.cleaned_data['last_name']

        if not self.cleaned_data['email']:
            user.email = ''
        else:
            user.email = self.cleaned_data['email']

        if commit:
            user.save()

        return user


class UserEditForm(ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


class BookCreateForm(ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'no_of_pages', 'genre', 'description']

        widgets = {
            'title': TextInput(attrs={'size': 70}),
            'author': TextInput(attrs={'size': 70}),
            'no_of_pages': NumberInput(attrs={'size': 5,
                                              'min': 0,
                                              'max': 10000}),
            'genre': TextInput(attrs={'size': 70}),
            'description': Textarea(attrs={'rows': 5,
                                           'cols': 68}),
        }
