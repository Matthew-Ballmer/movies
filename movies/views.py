import datetime
import json

from django.shortcuts import render
from django.http import Http404, HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.html import escape

from .models import TmdbMovie


class MovieType( object ):
    ALL = 'all'
    RELEASED = 'released'
    NOT_RELEASED = 'not-released'
    UNKNOWN = 'unknown'


MOVIES_ON_ONE_PAGE = 27
PAGES_RANGE_LEN = 3


def get_one_page(request, qs, items_on_page, range_len):
    """
    Return items for one page. Also return page numbers to display in paginator

    :param qs: queryset from which one page is taken (must be ordered!)

    :param items_on_page: number of items on one page
    :type items_on_page: int

    :param range_len: how many pages is shown "around" current page.
        e.g. for range_len = 2, page = 6:
            1 ... 4, 5, _6_, 7, 8 ... 10
    :type range_len: int

    :return: (items, page_numbers)
    :rtype: tuple

    page_numbers is a list with several iterable collections of integers
    e.g.:
        [[1, 2, 3], [45]]
        [[1], [4, 5, 6], [45]]
    """
    paginator = Paginator(qs, items_on_page, orphans=9)
    page = request.GET.get('page')
    try:
        items = paginator.page(page)
        current_page = int(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        items = paginator.page(1)
        current_page = 1
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        items = paginator.page(paginator.num_pages)
        current_page = paginator.num_pages
    except ValueError:
        items = paginator.page(1)
        current_page = 1

    if paginator.num_pages <= range_len:
        # 1, 2, 3, 4, 5, 6, _7_, 8, 9, 10
        page_numbers = [paginator.page_range]
    elif current_page <= range_len + 2:
        # _1_, 2, 3, ..., 10
        # 1, _2_, 3, 4, ... , 10
        # 1, 2, _3_, 4, 5, ..., 10
        # 1, 2, 3, _4_, 5, 6, ..., 10
        page_numbers = [
            range(1, current_page + range_len + 1),
            [paginator.num_pages]
        ]
    elif current_page >= paginator.num_pages - range_len - 2:
        # 1 ... 6, 7, _8_, 9, 10
        # 1 ... 5, 6, _7_, 8, 9, 10
        page_numbers = [
            [1],
            range(current_page - range_len, paginator.num_pages + 1)
        ]
    else:
        # 1 ... 4, 5, _6_, 7, 8 ... 10
        page_numbers = [
            [1],
            range(current_page - range_len, current_page + range_len + 1),
            [paginator.num_pages]
        ]
    return items, page_numbers


def get_movies(request, movies_type, as_list):
    """
    Return all movies page.

    :param movies_type: which movies to show
    :type movies_type: str (MovieType field)

    :param as_list: display as list if True, display as tile otherwise
    :type as_list: bool
    """
    if movies_type == MovieType.ALL:
        all_movies = TmdbMovie.objects.all().order_by('-us_physical_release_date')
    elif movies_type == MovieType.RELEASED:
        all_movies = TmdbMovie.objects.all().filter(
            us_physical_release_date__isnull=False
        ).filter(
            us_physical_release_date__lt=datetime.datetime.today()
        ).order_by(
            '-us_physical_release_date'
        )
    elif movies_type == MovieType.NOT_RELEASED:
        all_movies = TmdbMovie.objects.all().filter(
            us_physical_release_date__isnull=False
        ).filter(
            us_physical_release_date__gte=datetime.datetime.today()
        ).order_by(
            '-us_physical_release_date'
        )
    elif movies_type == MovieType.UNKNOWN:
        all_movies = TmdbMovie.objects.all().filter(
            us_physical_release_date__isnull=True
        ).order_by(
            '-release_date'
        )
    else:
        raise Http404("Movies type is not supported: {}".format(movies_type))

    if request.POST.get("search-field") is not None:
        search_query = escape(request.POST.get("search-field").strip())
        all_movies = all_movies.filter(title__icontains=search_query)

    movies, page_numbers = get_one_page(request, all_movies, MOVIES_ON_ONE_PAGE, PAGES_RANGE_LEN)
    context = {
        'movies_type': movies_type,
        'movies': movies,
        'page_numbers': page_numbers,
        'movies_count': all_movies.count(),
        'total_movies_count': TmdbMovie.objects.all().count(),
        'as_list': as_list,
    }
    if as_list:
        return render(request, 'movies/index_list.html', context)
    else:
        return render(request, 'movies/index.html', context)


def get_all_movies_as_tile(request):
    return get_movies(request, MovieType.ALL, as_list=False)


def get_all_movies_as_list(request):
    return get_movies(request, MovieType.ALL, as_list=True)


def get_released_movies_as_tile(request):
    return get_movies(request, MovieType.RELEASED, as_list=False)


def get_released_movies_as_list(request):
    return get_movies(request, MovieType.RELEASED, as_list=True)


def get_not_released_movies_as_tile(request):
    return get_movies(request, MovieType.NOT_RELEASED, as_list=False)


def get_not_released_movies_as_list(request):
    return get_movies(request, MovieType.NOT_RELEASED, as_list=True)


def get_unkn_release_movies_as_tile(request):
    return get_movies(request, MovieType.UNKNOWN, as_list=False)


def get_unkn_release_movies_as_list(request):
    return get_movies(request, MovieType.UNKNOWN, as_list=True)


def get_search_autocomplete(request):
    if request.is_ajax():
        search_query = escape(request.GET.get("term"))
        movies = TmdbMovie.objects.all().filter(title__icontains=search_query)[:10]
        movies_list = []
        for movie in movies:
            movies_list.append({
                'id': movie.id,
                'label': movie.title,
                'value': movie.title
            })
        data = json.dumps(movies_list)
    else:
        data = 'fail'
    return HttpResponse(data, 'application/json')
