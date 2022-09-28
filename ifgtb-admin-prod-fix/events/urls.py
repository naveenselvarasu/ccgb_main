
from django.urls import re_path
from events import views

urlpatterns = [
    re_path(r'^serve/latest/news/details/$', views.serve_latest_news_details),
    re_path(r'^serve/latest/news/details/for/portal/$', views.serve_latest_news_details_for_portal),
    re_path(r'^serve/active/events/$', views.serve_active_events),
    re_path(r'^serve/active/events/for/portal/$', views.serve_active_events_for_portal),
    re_path(r'^store/new/event/$', views.store_new_event),
    re_path(r'^serve/district/data/$', views.serve_district_data),
    re_path(r'^serve/district/data/portal/$', views.serve_district_data_portal),
    re_path(r'^store/news/$', views.store_news),
    re_path(r'^serve/advertisement/$', views.serve_advertisement),
    re_path(r'^serve/event/type/$', views.serve_event_type),
    re_path(r'^deactivate/news/$', views.deactivate_news),
    re_path(r'^deactivate/event/$', views.deactivate_event),
    re_path(r'^serve/state/district/taluks/$', views.serve_state_district_taluks),
    re_path(r'^show/news/$', views.show_news),
    re_path(r'^show/event/$', views.show_event),
    re_path(r'^serve/language/$', views.serve_language),
    re_path(r'^store/edit/new/event/portal/$', views.store_edit_new_event_portal),
]


