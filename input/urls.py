from django.conf.urls import url, include
from . import views
urlpatterns = [
    url(r'^bom/$', views.Bom.as_view(), name='bom'),
    url(r'^bom/add/$', views.BomAdd.as_view(), name='bom_add'),
]
