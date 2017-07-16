from django.conf.urls import url
from django.contrib.auth import views as auth_views

from . import views

app_name = 'movies'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^update/$', views.update, name='update'),
    url(r'^login/$', auth_views.LoginView.as_view(), name='login'),
    url(r'^logout/$', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
]