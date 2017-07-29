import django.utils.timezone
from django.db import models

from django.conf import settings

import tmdbsimple as tmdb
from ratelimit import rate_limited


class TmdbMovie(models.Model):
    # Necessary fields:
    id = models.IntegerField(verbose_name="TMDB id", primary_key=True)

    # Dates:
    update_time = models.DateTimeField(blank=True, null=True)
    release_date = models.DateField(blank=True, null=True)
    us_digital_release_date = models.DateField(blank=True, null=True)
    us_physical_release_date = models.DateField(blank=True, null=True)

    # Info:
    title = models.CharField(max_length=1024, blank=True, null=True)
    overview = models.TextField(blank=True, null=True)
    runtime = models.IntegerField(blank=True, null=True)
    imdb_id = models.CharField(verbose_name="iMDB id", max_length=32, blank=True, null=True)

    # Constants:
    class ReleaseType(object):
        PREMIERE = 1
        THEATRICAL_LIMITED = 2
        THEATRICAL = 3
        DIGITAL = 4
        PHYSICAL = 5
        TV = 6

    COUNTRY_ISO = 'iso_3166_1'

    API_WINDOW_DURATION = 10.0
    API_REQUESTS_LIMIT = 40

    def __str__(self):
        return u"{title} id{id}".format(**{
            'title': self.title,
            'id': self.id
        })

    @rate_limited(API_REQUESTS_LIMIT, API_WINDOW_DURATION)
    def update_info(self):
        tmdb.API_KEY = settings.TMDB_API_KEY
        moviesApi = tmdb.Movies()
        moviesApi.id = self.id
        res = moviesApi.info(append_to_response="release_dates")

        # Update dates:
        self.update_time = django.utils.timezone.now()
        self.release_date = moviesApi.release_date

        for result in moviesApi.release_dates['results']:
            if result[self.COUNTRY_ISO] == 'US':
                release_dates = result['release_dates']
                for release_date in release_dates:
                    if release_date['type'] == self.ReleaseType.DIGITAL:
                        self.us_digital_release_date = self._parse_date(release_date['release_date'])
                    elif release_date['type'] == self.ReleaseType.PHYSICAL:
                        self.us_physical_release_date = self._parse_date(release_date['release_date'])

        # Update info:
        self.title = moviesApi.title
        self.overview = moviesApi.overview
        self.runtime = moviesApi.runtime
        self.imdb_id = moviesApi.imdb_id

    def _parse_date(self, date_str):
        """Parse TMDB date expected in YYYY-MM-DD format"""
        year = int(date_str[0:4])
        month = int(date_str[5:7])
        day = int(date_str[8:10])
        return django.utils.timezone.datetime(year, month, day)
