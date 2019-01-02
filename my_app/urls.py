from django.conf.urls import url
from . import views
urlpatterns = [
    url(r'^item/bom/$', views.ItemBom.as_view(), name='item_bom'),
    url(r'^item/bom/add/$', views.ItemBomAdd.as_view(), name='item_bom_add'),
]
