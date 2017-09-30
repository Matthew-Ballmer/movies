import datetime

from django.core.management.base import BaseCommand

from ...models import TmdbMovie


class Command(BaseCommand):
    help = 'Update movies database through TMDB API'

    def handle(self, *args, **options):
        movies = TmdbMovie.objects.filter(us_physical_release_date__isnull=True)
        total = TmdbMovie.objects.all().count()
        i = 1
        print("[{}] Start movies update ...".format(datetime.datetime.now()))
        for movie in movies:
            print("[{} of {}] Updating movie: {} ...".format(i, total, movie.title))
            movie.update_info()
            movie.save()
            i += 1
