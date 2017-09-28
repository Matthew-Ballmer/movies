from django.core.management.base import BaseCommand, CommandError

from ...models import TmdbMovie


class Command(BaseCommand):
    help = 'Update movies database through TMDB API'

    def handle(self, *args, **options):
        TmdbMovie.add_movies(verbose=True)
