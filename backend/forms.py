from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UserChangeForm
from api.models import ApplicationUser


# Authentication Form
class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    username = forms.CharField(label="Nombre de Usuario", 
        max_length=128, 
        required=True, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de Usuario'}))
    
    password = forms.CharField(label="Contraseña",
        widget=forms.PasswordInput(render_value = True, attrs={'class': 'form-control', 'placeholder': 'Contraseña'}))


# Sign Up Form
class SignUpForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].label = 'Contraseña'
        self.fields['password2'].label = 'Confirmación de Contraseña'

    first_name = forms.CharField(label="Nombre", 
        max_length=128, 
        required=True, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'}))

    last_name = forms.CharField(label="Apellidos", 
        max_length=128, 
        required=True, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellidos'}))

    username = forms.CharField(label="Nombre de Usuario", 
        max_length=128, 
        required=True, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de Usuario'}))

    email = forms.EmailField(label="Correo Electrónico", 
        max_length=128, 
        required=True, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Correo Electrónico'}))
    
    company = forms.CharField(label="Entidad",
        max_length=128,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Entidad'}))

    password1 = forms.CharField(widget=forms.PasswordInput(render_value = True, attrs={'class': 'form-control', 'placeholder': 'Contraseña'}))
    password2 = forms.CharField(widget=forms.PasswordInput(render_value = True, attrs={'class': 'form-control', 'placeholder': 'Confirmación de Contraseña'}))

    class Meta:
        model = ApplicationUser
        fields = ['username', 'first_name', 'last_name', 'email', 'company', 'password1', 'password2']


# Update User Form
class UpdateUserForm(UserChangeForm):

    first_name = forms.CharField(label="Nombre", 
        max_length=128, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'}))

    last_name = forms.CharField(label="Apellidos", 
        max_length=128, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellidos'}))

    username = forms.CharField(label="Nombre de Usuario", 
        max_length=128, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de Usuario'}))

    email = forms.EmailField(label="Correo Electrónico", 
        max_length=128, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Correo Electrónico'}))
    
    company = forms.CharField(label="Entidad",
        max_length=128,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Entidad'}))

    password = forms.CharField(label="Contraseña",
        required=True,
        widget=forms.PasswordInput(render_value = True, attrs={'class': 'form-control', 'placeholder': 'Contraseña'}))

    class Meta:
        model = ApplicationUser
        fields = ['first_name', 'last_name', 'company', 'username', 'email', 'password']
