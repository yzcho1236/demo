from django.conf.urls import url, include
from . import views
urlpatterns = [
    url(r'^bom/$', views.Bom.as_view(), name='bom'),
    url(r'^bom/add/$', views.BomAdd.as_view(), name='bom_add'),
    url(r'^bom/edit/$', views.BomEdit.as_view(), name='bom_edit'),
    url(r'^bom/calculate/$', views.BomCalculate.as_view(), name='bom_calculate'),
]
