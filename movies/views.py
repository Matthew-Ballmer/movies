import datetime

from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.admin.views.decorators import staff_member_required

from .models import TmdbMovie


class MovieType( object ):
    ALL = 'all'
    RELEASED = 'released'
    NOT_RELEASED = 'not-released'
    UNKNOWN = 'unknown'


def get_all_movies(request):
    dvd_releases = TmdbMovie.objects.all().order_by('-us_physical_release_date')

    context = {
        'dvd_releases': dvd_releases,
        'movies_type': MovieType.ALL,
    }
    return render(request, 'movies/index.html', context)


def get_released_movies(request):
    dvd_releases = TmdbMovie.objects.all().filter(
        us_physical_release_date__isnull=False
    ).filter (
        us_physical_release_date__lt=datetime.datetime.today()
    ).order_by(
        '-us_physical_release_date'
    )
    context = {
        'dvd_releases': dvd_releases,
        'movies_type': MovieType.RELEASED,
    }
    return render(request, 'movies/index.html', context)

@staff_member_required
def update(request):
    movies = TmdbMovie.objects.filter(us_physical_release_date__isnull=True)
    for movie in movies:
        movie.update_info()
        movie.save()
        # print("updated movie: {}".format(movie.title))

    return HttpResponseRedirect(reverse('movies:index'))


@staff_member_required
def add_movies(request):
    TmdbMovie.add_movies()
    return HttpResponseRedirect(reverse('movies:index'))
