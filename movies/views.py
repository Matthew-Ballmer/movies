from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse

from django.conf import settings

from .models import TmdbMovie


def index(request):
    dvd_releases = TmdbMovie.objects.filter(
        us_physical_release_date__isnull=False
    ).order_by(
        'us_physical_release_date'
    )

    unknown_dvd_releases = TmdbMovie.objects.exclude(
        us_physical_release_date__isnull=False
    ).order_by(
        'release_date'
    )

    context = {
        'dvd_releases': dvd_releases,
        'unknown_dvd_releases': unknown_dvd_releases,
        'MEDIA_URL': settings.MEDIA_URL,
    }
    return render(request, 'movies/index.html', context)


def update(request):
    movies = TmdbMovie.objects.filter(us_physical_release_date__isnull=True)
    for movie in movies:
        movie.update_info()
        movie.save()
        # print("updated movie: {}".format(movie.title))

    return HttpResponseRedirect(reverse('movies:index'))
