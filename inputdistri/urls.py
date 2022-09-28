from django.conf.urls import url
from inputdistri import views

urlpatterns = [
    url(r'^serve/harvest/level/$', views.serve_harvest_level),
    url(r'^register/harvest/$', views.register_harvest),
    url(r'^serve/weight/loss/percentage/$', views.serve_weight_loss_percentage),
]

