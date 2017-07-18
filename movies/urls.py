from django.conf.urls import url

from . import views

app_name = 'movies'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^update/$', views.update, name='update'),
]
