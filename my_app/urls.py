from django.conf.urls import url
from rest_framework.routers import DefaultRouter

from . import views
urlpatterns = [
    url(r'^item/bom/$', views.ItemBom.as_view(), name='item_bom'),
    url(r'^item/bom/add/$', views.ItemBomAdd.as_view(), name='item_bom_add'),
    url(r'^item/bom/edit/$', views.ItemBomEdit.as_view(), name='item_bom_edit'),
    url(r'^item/bom/delete/$', views.ItemBomDelete.as_view(), name='item_bom_delete'),
    url(r'^item/bom/calculate/$', views.ItemBomCalculate.as_view(), name='item_bom_calculate'),
    url(r'^upload/$', views.UploadView.as_view(), name='upload'),
    url(r'^enum/$', views.EnumView.as_view(), name='get_enum'),
    url(r'^test/$', views.JustTest.as_view(), name='test'),
]
# router = DefaultRouter()  # 可以处理视图的路由器
# # router.register(r'info', views.InfoViewSet)  # 向路由器中注册视图集
# urlpatterns += router.urls
