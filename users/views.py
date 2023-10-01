from django.shortcuts import render
from .forms import LoginForm

def sign_in(request):
    if (request.method == 'GET'):
        form = LoginForm()
        return render(request, 'login.html', {'form': form})