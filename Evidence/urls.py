"""Evidence URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from repository import views as repo
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve as staticserve

urlpatterns = [
    url(r'^repository/', include('repository.urls')),
    url(r'^$', repo.homepage),
    url(r'^editdigital/', repo.addDigital),
    url(r'^deletedigital/', repo.deleteDigital),
    url(r'^editelectronic/', repo.addElectronic),
    url(r'^deleteelectronic/', repo.deleteElectronic),
    url(r'^add/', repo.addRepo),
    url(r'^deleterepository/', repo.delRepo),
    url(r'^login/', repo.login, name='login'),
    url(r'^register/$', repo.reg, name='register'),
    url(r'^logout/$', repo.logout, name='logout'),
    url(r'^register/success/', repo.register_success, name='success'),
    url(r'^repository/$', repo.viewRepo),
    url(r'^repository/view/$', repo.viewRepo),
    url(r'^repository/view/edit/(?P<pk>\w+)/$', repo.editRepo),
    url(r'^repository/view/(?P<pk>\w+)/$', repo.detail),



] + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)

urlpatterns += [
    url(r'^api-auth/', include('rest_framework.urls',
                               namespace='rest_framework')),
]

if settings.DEBUG is False:
    urlpatterns += [url(r'^media/(?P<path>.*)$', staticserve, {'document_root': settings.MEDIA_ROOT,}),
                    url(r'^static/(?P<path>.*)$', staticserve, {'document_root': settings.STATIC_ROOT}),]
elif settings.DEBUG is True:
    urlpatterns += [url(r'^media/(?P<path>.*)$', staticserve, {'document_root': settings.MEDIA_ROOT,}),
                    url(r'^static/(?P<path>.*)$', staticserve, {'document_root': settings.STATIC_ROOT}), ]