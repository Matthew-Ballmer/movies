from django.contrib import admin

from .models import OmdbMovie, TmdbMovie


admin.site.register(OmdbMovie)
admin.site.register(TmdbMovie)
