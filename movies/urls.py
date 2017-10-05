from django.conf.urls import url

from . import views

app_name = 'movies'
urlpatterns = [
    url(r'^$', views.get_all_movies_as_tile, name='index'),
    url(r'^list/$', views.get_all_movies_as_list, name='list-index'),

    url(r'^released/$', views.get_released_movies_as_tile, name='get-released'),
    url(r'^list/released/$', views.get_released_movies_as_list, name='get-released'),

    url(r'^not-released/$', views.get_not_released_movies_as_tile, name='get-not-released'),
    url(r'^list/not-released/$', views.get_not_released_movies_as_list, name='get-not-released'),

    url(r'^unknown/$', views.get_unkn_release_movies_as_tile, name='get-unknown'),
    url(r'^list/unknown/$', views.get_unkn_release_movies_as_list, name='get-unknown'),

    url(r'^search-autocomplete/$', views.get_search_autocomplete, name='search-autocomplete'),
]
