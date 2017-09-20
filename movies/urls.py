from django.conf.urls import url

from . import views

app_name = 'movies'
urlpatterns = [
    url(r'^$', views.get_all_movies, name='index'),
    url(r'^update/$', views.update, name='update'),
    url(r'^add-movies/$', views.add_movies, name='add-movies'),
    url(r'^released/$', views.get_released_movies, name='get-released'),
    url(r'^not-released/$', views.get_not_released_movies, name='get-not-released'),
    url(r'^unknown/$', views.get_unkn_release_movies, name='get-unknown'),
]
