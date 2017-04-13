from datetime import datetime
import urllib
from urllib import parse, request
import json
import datetime

from django.utils import timezone
from django.db import models


class Movie(models.Model):
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
    update_date = models.DateTimeField(default=timezone.now())
    is_info_received = models.BooleanField(default=False)
    full_info_json = models.TextField(default='')
    dvd_release_date_status = models.CharField(default=NOT_RECEIVED,
                                               max_length=2,
                                               choices=DVD_DATE_STATUS_CHOICE)
    dvd_release_date = models.DateField(default=timezone.now())
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
                    parsed_date = Movie.parse_omdb_date(self.raw_dvd_release_date)
                    if parsed_date is not None:
                        self.dvd_release_date_status = self.VALID_DATE
                        self.dvd_release_date = parsed_date
                    else:
                        self.dvd_release_date_status = self.NOT_PARSED
            else:
                self.dvd_release_date_status = self.NOT_RECEIVED

        self.update_date = timezone.now()

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