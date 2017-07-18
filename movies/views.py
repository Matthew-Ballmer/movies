from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm

from .models import Movie


def index(request):
    dvd_releases = Movie.objects.filter(
        dvd_release_date_status=Movie.VALID_DATE
    ).order_by(
        'dvd_release_date'
    )

    unknown_dvd_releases = Movie.objects.exclude(
        dvd_release_date_status=Movie.VALID_DATE
    ).order_by(
        'dvd_release_date_status'
    )

    context = {
        'dvd_releases': dvd_releases,
        'unknown_dvd_releases': unknown_dvd_releases
    }
    return render(request, 'movies/index.html', context)


def update(request):
    movies = Movie.objects.all()
    for movie in movies:
        movie.download_info()
        movie.save()

    return HttpResponseRedirect(reverse('movies:index'))


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(request, username=username, password=raw_password)
            if user is None:
                return render(request, 'auth/signup_fail.html', {})
            else:
                login(request, user)
                return redirect('/')
    else:
        form = UserCreationForm()
    return render(request, "auth/signup.html", {'form': form})
