from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse

from .models import OmdbMovie
from .models import TmdbMovie


def index(request):
    dvd_releases = OmdbMovie.objects.filter(
        dvd_release_date_status=OmdbMovie.VALID_DATE
    ).order_by(
        'dvd_release_date'
    )

    unknown_dvd_releases = OmdbMovie.objects.exclude(
        dvd_release_date_status=OmdbMovie.VALID_DATE
    ).order_by(
        'dvd_release_date_status'
    )

    context = {
        'dvd_releases': dvd_releases,
        'unknown_dvd_releases': unknown_dvd_releases
    }
    return render(request, 'movies/index.html', context)


def update(request):
    movies = TmdbMovie.objects.filter(us_physical_release_date__isnull=True)
    for movie in movies:
        movie.update_info()
        movie.save()
        # print("updated movie: {}".format(movie.title))

    return HttpResponseRedirect(reverse('movies:index'))
