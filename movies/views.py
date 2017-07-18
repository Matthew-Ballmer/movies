from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse

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
