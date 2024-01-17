
from django.contrib import admin
from django.urls import path
from . import views
urlpatterns = [
    path('', views.base, name='base'),
    path('vkeepexcel', views.vkeepexcel,name='vkeepexcel'),
    path('handlevkeep', views.handlevkeep,name='handlevkeep'),
]
