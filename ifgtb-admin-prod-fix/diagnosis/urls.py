from django.urls import re_path
from diagnosis import views

urlpatterns = [
    re_path(r'^serve/crop/list/$', views.serve_crop_list),
    re_path(r'^register/user/query/$', views.register_user_query),
    re_path(r'^serve/user/query/history/$', views.serve_user_query_history),
    re_path(r'^serve/query/history/for/admin/$', views.serve_query_history_for_admin),
    re_path(r'^get/recommendation/data/for/update/$', views.get_recommendation_data_for_update),
    re_path(r'^store/recommendations/$', views.store_recommendations),
    re_path(r'^check/for/pending/queries/$', views.check_for_pending_queries),
    re_path(r'^approve/recommendation/$', views.approve_recommendation),
    re_path(r'^disapprove/recommendation/$', views.disapprove_recommendation),
    re_path(r'^serve/expert/list/$', views.serve_expert_list),
    re_path(r'^assign/query/to/users/$', views.assign_query_to_users),
    re_path(r'^ask/expert/is/system/assingned/$', views.ask_expert_is_system_assigned),
    re_path(r'^serve/user/query/history/for/scientist/$', views.serve_user_query_history_for_scientist),
    re_path(r'^register/recommendation/from/scientist/$', views.register_recommendation_from_scientist),
    re_path(r'^store/circulars/$', views.store_circulars),
    re_path(r'^serve/circulars/$', views.serve_circulars),
    re_path(r'^serve/circulars/mobile/$', views.serve_circulars_mobile),
    re_path(r'^show/circular/$', views.show_circular),
    re_path(r'^serve/circular/types/$', views.serve_circular_types),
    re_path(r'^save/query/assignto/scientist/$', views.save_query_assign_to_scientist),
]
