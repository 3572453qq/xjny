
from django.contrib import admin
from django.urls import path
from . import views
urlpatterns = [
    path('', views.base, name='base'),
    path('vkeepexcel', views.vkeepexcel,name='vkeepexcel'),
    path('handlevkeep', views.handlevkeep,name='handlevkeep'),
    path('cyclesort', views.cyclesort,name='cyclesort'),
    path('handlecycle', views.handlecycle,name='handlecycle'),
    path('base_test', views.base_test,name='base_test'),
    path('cycles', views.cycles,name='cycles'),
    path('handlecrate', views.handlecrate,name='handlecrate'),
    path('crate', views.crate,name='crate'),
]
