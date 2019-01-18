from django.conf.urls import url, include
from . import views
urlpatterns = [
    url(r'^api/item/$', views.ItemAPIView.as_view(), name='api_item'),
    url(r'^api/item/(?P<pk>(.+))/$', views.ItemDetailView.as_view(), name='api_item_detail'),
    url(r'^api/bom/$', views.BomAPIView.as_view(), name='api_bom'),
    url(r'^api/bom/(?P<pk>(.+))/$', views.BomDetailView.as_view(), name='api_bom_detail'),
    url(r'^api/calculate/bom/$', views.BomCalculateView.as_view(), name='api_bom_calculate'),
]