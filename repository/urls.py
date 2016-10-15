from django.conf.urls import url
from repository import views
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    url(r'api-root/', views.api_root, name='api-root'),
    url(r'^xml/$', views.RepositoryList.as_view(), name='repository-list'),
    url(r'^xml/(?P<pk>\w+)/$', views.RepositoryDetail.as_view(), name='repository-detail'),
    url(r'^xml/digital/$', views.DigitalList.as_view(), name='digital-list'),
    url(r'^xml/digital/(?P<pk>\w+)/$', views.DigitalDetail.as_view(), name='digital-detail'),
    url(r'^xml/electronic/$', views.ElectronicList.as_view(), name='electronic-list'),
    url(r'^xml/electronic/(?P<pk>\w+)/$', views.ElectronicDetail.as_view(), name='electronic-detail'),
    url(r'^users/$', views.UserList.as_view(), name='user-list'),
    url(r'^users/(?P<pk>\w+)/$', views.UserDetail.as_view(), name='user-detail'),
]

urlpatterns = format_suffix_patterns(urlpatterns)