from django.shortcuts import render, redirect, reverse
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(request, username=username, password=raw_password)
            if user is None:
                return redirect(reverse('core:signup-fail'))
            else:
                login(request, user)
                return redirect(reverse('movies:index'))
    else:
        form = UserCreationForm()
    return render(request, "auth/signup.html", {'form': form})


def signup_fail(request):
    return render(request, 'auth/signup_fail.html', {})
