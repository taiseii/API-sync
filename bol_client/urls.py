from django.urls import path, include, re_path
from . import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register('shop_credentials', views.ShopCredentialsView)
router.register('shipments', views.ShipmentsView)
router.register('shipments_item', views.ShipmentsItemsView)
router.register('transport', views.TransportSerializerView)
router.register('customer_details', views.CustomerDetailsSerializerView)

router.register('token_request_log', views.tokenRequestLogSerializerView)
router.register('shop_request_log', views.shopRequestLogSerializerView)


urlpatterns = [
    path('', include(router.urls)),
    path('update_shipment', views.UpdateShipmentView.as_view()),
    re_path(r'^test_get_shipment/(?P<page>)/?$', views.test_get_shipment),
    path('test_get_shipment_detail/<int:pk>', views.test_get_shipment_detail)
]