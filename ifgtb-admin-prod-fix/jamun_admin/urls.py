from cms.sitemaps import CMSSitemap
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, re_path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.static import serve

admin.autodiscover()

urlpatterns = [
    re_path("sitemap.xml", sitemap, {"sitemaps": {"cmspages": CMSSitemap}}),
    re_path(r'^admin/', admin.site.urls),  # NOQA
    re_path(r"^events/", include("events.urls")),
    # re_path(r'^taggit_autosuggest/', include('taggit_autosuggest.urls')),
]



urlpatterns += (
    re_path(r'^main/', include('main.urls')), 
    re_path(r'^diagnosis/', include('diagnosis.urls')),
    re_path(r'^yield_calculator/', include('yield_calculator.urls')),
    re_path(r'^', include('cms.urls')),

)


# This is only needed when using runserver.
if settings.DEBUG:
    urlpatterns = [
        re_path(r'^media/(?P<path>.*)$', serve,
            {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
        ] + staticfiles_urlpatterns() + urlpatterns
