from django.conf.urls import url
from . import views
urlpatterns = [
    url(r'^item/bom/$', views.ItemBom.as_view(), name='item_bom'),
    url(r'^item/bom/add/$', views.ItemBomAdd.as_view(), name='item_bom_add'),
    url(r'^item/bom/edit/$', views.ItemBomEdit.as_view(), name='item_bom_edit'),
    url(r'^item/bom/delete/$', views.ItemBomDelete.as_view(), name='item_bom_delete'),
    url(r'^item/bom/calculate/$', views.ItemBomCalculate.as_view(), name='item_bom_calculate'),
    url(r'^test/$', views.JustTest.as_view(), name='test'),
    url(r'^test1/$', views.ShowPicture.as_view(), name='picture'),
]
