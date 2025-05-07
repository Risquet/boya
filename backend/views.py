from django.conf import settings
from django.shortcuts import render, redirect, HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.core.mail import EmailMessage
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from .forms import LoginForm, SignUpForm
from api.models import Buoy, Parameter, News


def home(request):
    parameters = Parameter.objects.all()
    return render(request, 'index.html', {'parameters': parameters})


def buoys(request):
    buoys = Buoy.objects.all()
    return render(request, 'buoys.html', {'buoys': buoys})


def buoy(request, buoy_id):
    buoy = Buoy.objects.filter(id=buoy_id).first()
    parameters = buoy.parameters.all()
    return render(request, 'buoy.html', {'buoy': buoy, 'parameters': parameters})


def multicharts(request, buoy_id):
    buoy = Buoy.objects.filter(id=buoy_id).first()
    parameters = request.GET.get('parameters').split(",")
    parameters = buoy.parameters.filter(id__in=parameters).all()
    return render(request, 'multicharts.html', { 'buoy': buoy, 'parameters': parameters })


def stackedcharts(request, buoy_id):
    buoy = Buoy.objects.filter(id=buoy_id).first()
    parameters = request.GET.get('parameters').split(",")
    parameters = buoy.parameters.filter(id__in=parameters).all()
    return render(request, 'stackedcharts.html', { 'buoy': buoy, 'parameters': parameters })


def chartjs(request):
    parameters = Parameter.objects.all()
    return render(request, 'index_chartjs.html', {'parameters': parameters})


def uplot(request):
    parameters = Parameter.objects.all()
    return render(request, 'index_uplot.html', {'parameters': parameters})


def echarts(request):
    parameters = Parameter.objects.all()
    return render(request, 'index_echarts.html', {'parameters': parameters})


def map(request):
    buoys = Buoy.objects.all()
    return render(request, 'map.html', {'buoys': buoys})


def news(request):
    newslist = News.objects.all()
    return render(request, 'news.html', {'newslist': newslist})


def entrar(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('/map/')
    if request.method == 'GET':
        form = LoginForm()
        return render(request, 'login.html', {'form': form})
    if request.method == 'POST':
        form = LoginForm(request=request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return HttpResponseRedirect('/')
        return render(request, 'login.html', {'form': form})


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = get_user_model().objects.get(pk=uid)
    except Exception as e:
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Cuenta activada correctamente.')
        return redirect('/login/')
    else:
        return HttpResponse('El enlace de activación no es válido.')


def activateEmail(request, user, to_email):
    subject = 'Activa tu cuenta'
    protocol = getattr(settings, 'EMAIL_SITE_PROTOCOL', 'https')
    domain = getattr(settings, 'EMAIL_DOMAIL', 'boya01.citmatel.inf.cu')

    message = render_to_string('email_activation.html', {
        'user': user,
        'domain': domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': default_token_generator.make_token(user),
        'protocol': protocol
    })
    email = EmailMessage(subject, message, to=[to_email])
    try:
        if email.send():
            messages.success(request, 'Correo enviado, revisa tu bandeja de entrada para activar tu cuenta.')
            return True
        else:
            messages.error(request, 'Error al enviar el correo, intenta de nuevo.')
            return False
    except Exception as e:
        print(e)
        messages.error(request, 'Error al enviar el correo: {error}.'.format(error=e))
        return False


def registrar(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('/map/')
    if request.method == 'GET':
        form = SignUpForm()
        return render(request, 'register.html', {'form': form})
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            if not activateEmail(request, user, user.email):
                user.delete()
            else:
                return redirect('/login/')
        return render(request, 'register.html', {'form': form})


def resetPassword(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = get_user_model().objects.get(pk=uid)
    except Exception as e:
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'GET':
            return render(request, 'reset_password.html')
        if request.method == 'POST':
            password = request.POST.get('new_password')
            user.set_password(password)
            user.save()
            messages.success(request, 'Contraseña restablecida correctamente.')
            return redirect('/login/')
    else:
        return HttpResponse('El enlace de restablecimiento de contraseña no es válido.')


def sendResetPasswordEmail(request, user, to_email):
    subject = 'Restablece tu contraseña'
    protocol = getattr(settings, 'EMAIL_SITE_PROTOCOL', 'boya01.citmatel.inf.cu')
    domain = getattr(settings, 'EMAIL_DOMAIL', 'https')

    message = render_to_string('email_reset_password.html', {
        'user': user,
        'domain': domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': default_token_generator.make_token(user),
        'protocol': protocol
    })
    email = EmailMessage(subject, message, to=[to_email])
    try:
        if email.send():
            messages.success(request, 'Correo enviado, revisa tu bandeja de entrada para restablecer tu contraseña.')
            return True
        else:
            messages.error(request, 'Error al enviar el correo, intenta de nuevo.')
            return False
    except Exception as e:
        print(e)
        messages.error(request, 'Error al enviar el correo: {error}.'.format(error=e))
        return False


def forgotPassword(request):
    if request.method == 'GET':
        return render(request, 'forgot_password.html')
    if request.method == 'POST':
        email = request.POST.get('email')
        user = get_user_model().objects.filter(email=email).first()
        if user is not None:
            sendResetPasswordEmail(request, user, email)
        else:
            messages.error(request, 'No existe un usuario con ese correo.')
        return render(request, 'forgot_password.html')


@login_required(login_url='/login')
def salir(request):
    logout(request)
    return redirect("/")
