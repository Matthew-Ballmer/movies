from django.core.management.base import BaseCommand, CommandError

from ...models import TmdbMovie


class Command(BaseCommand):
    help = 'Update movies database through TMDB API'

    def handle(self, *args, **options):
        movies = TmdbMovie.objects.filter(us_physical_release_date__isnull=True)
        for movie in movies:
            print("Updating movie: {} ...".format(movie.title))
            movie.update_info()
            movie.save()
