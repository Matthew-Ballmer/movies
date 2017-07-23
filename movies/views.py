import time
import datetime

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
    movies = TmdbMovie.objects.all()

    # Limits:
    window_duration = datetime.timedelta(seconds=10)
    request_limit = 40

    # Current counters:
    window_start = datetime.datetime.now()
    request_count = 0

    for movie in movies:
        now = datetime.datetime.now()
        request_count += 1
        if (now - window_start <= window_duration) and (request_count > request_limit):
            # Enough requests, wait for the new window:
            sleep_time = window_start + window_duration - now
            time.sleep(sleep_time.seconds)
            # Reset window:
            window_start = datetime.datetime.now()
            request_count = 0
        movie.update()
        movie.save()
    return HttpResponseRedirect(reverse('movies:index'))
