import time
import datetime
import urllib
from urllib import parse, request
import json

import django.utils.timezone
from django.db import models
from django.db.models import Q

import tmdbsimple as tmdb

from .secret_settings import TMDB_API_KEY


class TmdbManager(models.Manager):
    # TMDB API limits:
    API_WINDOW_DURATION = datetime.timedelta(seconds=10)
    API_REQUESTS_LIMIT = 40

    def update_dvd_dates(self):
        # Current counters:
        window_start = datetime.datetime.now()
        request_count = 0

        movies = self.filter(Q(us_physical_release_date__isnull=True) |
                             Q(us_digital_release_date__isnull=True))

        for movie in movies:
            now = datetime.datetime.now()
            request_count += 1
            if ( now - window_start <= self.API_WINDOW_DURATION ) and \
               ( request_count > self.API_REQUESTS_LIMIT ):
                # Limit exceeded, enough requests, wait for the new window:
                sleep_time = window_start + self.API_WINDOW_DURATION - now
                time.sleep(sleep_time.seconds)
                # Reset window:
                window_start = datetime.datetime.now()
                request_count = 0
            movie.update_info()
            movie.save()


class TmdbMovie(models.Model):
    # Custom manager:
    objects = TmdbManager()

    # Necessary fields:
    id = models.IntegerField(verbose_name="TMDB id", primary_key=True)

    # Dates:
    update_date = models.DateField(blank=True, null=True)
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

    def __str__(self):
        return u"{title} id{id}".format(**{
            'title': self.title,
            'id': self.id
        })

    def update_info(self):
        tmdb.API_KEY = TMDB_API_KEY
        moviesApi = tmdb.Movies()
        moviesApi.id = self.id
        res = moviesApi.info(append_to_response="release_dates")

        # Update dates:
        self.update_date = django.utils.timezone.now()
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


class OmdbMovie(models.Model):
    N_A = 'NA'
    NOT_RECEIVED = 'NF'
    NOT_PARSED = 'NP'
    VALID_DATE = 'R'

    DVD_DATE_STATUS_CHOICE = (
        (N_A, 'N/A'),
        (NOT_RECEIVED, 'not received'),
        (NOT_PARSED, "couldn't parse"),
        (VALID_DATE, 'valid date received'),
    )

    title = models.CharField(max_length=1024)
    year = models.DateField()  # TODO: field with only year editable

    # movie info:
    update_date = models.DateTimeField(default=django.utils.timezone.now)
    is_info_received = models.BooleanField(default=False)
    full_info_json = models.TextField(default='')
    dvd_release_date_status = models.CharField(default=NOT_RECEIVED,
                                               max_length=2,
                                               choices=DVD_DATE_STATUS_CHOICE)
    dvd_release_date = models.DateField(default=django.utils.timezone.now)
    raw_dvd_release_date = models.CharField(default='',
                                            max_length=32)

    def __str__(self):
        if self.dvd_release_date_status == self.VALID_DATE:
            return '"{}", dvd release: {}'.format(self.title,
                                                  self.dvd_release_date)
        elif self.dvd_release_date_status == self.NOT_PARSED:
            return  '"{}", not parsed dvd release date: {}'.format(self.title,
                                                                   self.raw_dvd_release_date)
        else:
            return '"{}", dvd release: {}'.format(self.title,
                                                  self.dvd_release_date_status)

    def download_info(self):
        # ombd API constants:
        API_URL = "http://www.omdbapi.com/?"
        TITLE_KEY = 't'
        YEAR_KEY = 'y'
        DVD_DATE_KEY = 'DVD'
        RESPONSE_SUCCESS_KEY = 'Response'
        TRUE_STR = 'True'
        NA_STR = 'N/A'

        movie_request_dict = {
            TITLE_KEY: self.title,
            YEAR_KEY: self.year.year,
        }
        get_params = urllib.parse.urlencode(movie_request_dict)
        request = ''.join((API_URL, get_params))
        response_json = urllib.request.urlopen(request).read()
        response = json.loads(response_json)
        self.full_info_json = response
        self.is_info_received = (response[RESPONSE_SUCCESS_KEY] == TRUE_STR)

        if self.is_info_received:
            if DVD_DATE_KEY in response.keys():
                self.raw_dvd_release_date = response[DVD_DATE_KEY]

                if self.raw_dvd_release_date == NA_STR:
                    self.dvd_release_date_status = self.N_A
                else:
                    parsed_date = OmdbMovie.parse_omdb_date(self.raw_dvd_release_date)
                    if parsed_date is not None:
                        self.dvd_release_date_status = self.VALID_DATE
                        self.dvd_release_date = parsed_date
                    else:
                        self.dvd_release_date_status = self.NOT_PARSED
            else:
                self.dvd_release_date_status = self.NOT_RECEIVED

        self.update_date = django.utils.timezone.now()

    @classmethod
    def parse_omdb_date(cls, date_str):
        """
        Method parses string date and returns a datetime object or None
        
        :param date_str: date string in format: '21 Mar 2017' 
        :return: datetime object or None
        """

        month_table = {
            'Jan': 1,
            'Feb': 2,
            'Mar': 3,
            'Apr': 4,
            'May': 5,
            'Jun': 6,
            'Jul': 7,
            'Aug': 8,
            'Sep': 9,
            'Oct': 10,
            'Nov': 11,
            'Dec': 12
        }

        day_month_year_count = 3

        day_index = 0
        month_index = 1
        year_index = 2

        date = date_str.split()

        if len(date) != day_month_year_count:
            return None

        month_str = date[month_index]

        if month_str not in month_table.keys():
            return None
        else:
            month = month_table[month_str]

        try:
            year = int(date[year_index])
        except ValueError:
            return None

        try:
            day = int(date[day_index])
        except ValueError:
            return None

        return datetime.datetime(year=year, month=month, day=day)