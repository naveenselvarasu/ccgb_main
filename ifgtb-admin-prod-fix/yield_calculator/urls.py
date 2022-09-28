from django.urls import re_path
from yield_calculator import views

urlpatterns = [
    re_path(r'^test/url/$', views.test_url),
    re_path(r'^serve/clone/for/calculation/$', views.serve_clone_for_calculation),
    re_path(r'^calculate/and/record/yield/value/$', views.calculate_and_record_yield_value),
    re_path(r'^send/yield/result/message/$', views.send_yield_result_message),
    re_path(r'^serve/formula/for/clone/$', views.serve_formula_for_clone),
    re_path(r'^register/individual/yield/calculation/value/$', views.register_individual_yield_calculation_value),
]
