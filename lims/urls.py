
from django.contrib import admin
from django.urls import path
from . import views
from . import cycleprocess
urlpatterns = [
    path('', views.base, name='base'),
    path('vkeepexcel', views.vkeepexcel,name='vkeepexcel'),
    path('handlevkeep', views.handlevkeep,name='handlevkeep'),
    # path('cyclesort', views.cyclesort,name='cyclesort'),
    path('handlecycle', views.handlecycle,name='handlecycle'),
    path('base_test', views.base_test,name='base_test'),
    path('cycles', views.cycles,name='cycles'),
    path('handlecrate', views.handlecrate,name='handlecrate'),
    path('crate', views.crate,name='crate'),
    # path('querycycle', views.querycycle,name='querycycle'),
    # path('getcycledata', views.getcycledata,name='getcycledata'),
    path('cyclesummary', cycleprocess.cyclesummary,name='cyclesummary'),
    path('handlecyclesummary', cycleprocess.handlecyclesummary,name='handlecyclesummary'),
    path('cycledetail', cycleprocess.cycledetail,name='cycledetail'),
    path('cyclebybarcode', cycleprocess.cyclebybarcode,name='cyclebybarcode'),
    path('handlecyclebarcode', cycleprocess.handlecyclebarcode,name='handlecyclebarcode'),
    path('vhrjoindate', views.vhrjoindate,name='vhrjoindate'),
    path('handlehrjoindate', views.handlehrjoindate,name='handlehrjoindate'),
]
