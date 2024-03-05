
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from django.views.generic import RedirectView
from lims.views import mylogout

# from django.conf.urls import url

urlpatterns = [
    path('admin/logout/', mylogout, name='mylogout'),
    path('admin/', admin.site.urls),
    path('accounts/',include('django.contrib.auth.urls')), 
    path('lims/',include('lims.urls')),
    path('', RedirectView.as_view(url='/lims/index')),
      
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)