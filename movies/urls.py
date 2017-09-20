from django.conf.urls import url

from . import views

app_name = 'movies'
urlpatterns = [
    url(r'^$', views.get_all_movies, name='index'),
    url(r'^update/$', views.update, name='update'),
    url(r'^add-movies/$', views.add_movies, name='add-movies'),
    url(r'^released/$', views.get_released_movies, name='get-released'),
]
