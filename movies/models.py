import sys
import dateutil.parser
from requests.exceptions import HTTPError

import django.utils.timezone
from django.db import models

from django.conf import settings

import tmdbsimple as tmdb
from ratelimit import rate_limited

from .exceptions import MovieDateError


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
        try:
            moviesApi.info(append_to_response="release_dates")
        except HTTPError as ex:
            print("Update movie failed: {}".format(self.title), file=sys.stderr)
            print(ex)
            return

        # Update dates:
        self.update_time = django.utils.timezone.now()
        try:
            self.release_date = self._parse_date(moviesApi.release_date)
        except MovieDateError:
            print("Couldn't parse release date: '{}'".format(moviesApi.release_date), file=sys.stderr)

        for result in moviesApi.release_dates['results']:
            if result[self.COUNTRY_ISO] == 'US':
                release_dates = result['release_dates']
                for release_date in release_dates:
                    if release_date['type'] == self.ReleaseType.DIGITAL:
                        try:
                            self.us_digital_release_date = self._parse_date(release_date['release_date'])
                        except MovieDateError:
                            print("Couldn't parse US digital release date: '{}'".format(release_date['release_date']),
                                  file=sys.stderr)
                            self.us_digital_release_date = None
                    elif release_date['type'] == self.ReleaseType.PHYSICAL:
                        try:
                            self.us_physical_release_date = self._parse_date(release_date['release_date'])
                        except MovieDateError:
                            print("Couldn't parse US physical release date: '{}'".format(release_date['release_date']),
                                  file=sys.stderr)
                            self.us_physical_release_date = None

        # Update info:
        self.title = moviesApi.title
        self.overview = moviesApi.overview
        self.runtime = moviesApi.runtime
        self.imdb_id = moviesApi.imdb_id

    @staticmethod
    def _parse_date(date_str):
        """Parse TMDB date expected in YYYY-MM-DD format

        :raise: MovieDateError
        """
        try:
            date = dateutil.parser.parse(date_str)
        except ValueError:
            raise MovieDateError()
        return date

    @classmethod
    def add_movies(cls, verbose):
        tmdb.API_KEY = settings.TMDB_API_KEY
        moviesApi = tmdb.Movies()
        total_pages = cls.get_now_playing_first_page(moviesApi)

        # Parse first page:
        for movie in moviesApi.results:
            TmdbMovie.create_movie_if_new(movie['id'], movie['title'], verbose)

        # Parse the rest of pages:
        for page in range(2, total_pages + 1, 1):
            cls.get_now_playing_nth_page(moviesApi, page)

            for movie in moviesApi.results:
                TmdbMovie.create_movie_if_new(movie['id'], movie['title'], verbose)

    @classmethod
    @rate_limited(API_REQUESTS_LIMIT, API_WINDOW_DURATION)
    def get_now_playing_first_page(cls, moviesApi):
        moviesApi.now_playing()
        return moviesApi.total_pages

    @classmethod
    @rate_limited(API_REQUESTS_LIMIT, API_WINDOW_DURATION)
    def get_now_playing_nth_page(cls, moviesApi, page):
        moviesApi.now_playing(page=page)

    @classmethod
    def create_movie_if_new(cls, id, title, verbose):
        """If movie with such id does not exist, then create one"""
        if 0x00 == TmdbMovie.objects.filter(id=id).count():
            newMovie = TmdbMovie(id=id, title=title)
            newMovie.save()
            if verbose:
                print("Added movie: {}".format(title))

