from django.test import TestCase
from django.http import HttpResponse
import requests
import timeit
import json
from .tasks import RequestHandler
from .models import ShopCredentials
from .serializers import ShopCredentialsSerializer


# class RequestHandlerTestCase(TestCase):
#     def test_refresh_token(TestCase):
#         ShopName='dope'
#         # da_shop = ShopCredentials.objects.filter(shopId=2)
#         da_shop = ShopCredentials({"shopName":"test", "clientId":173, "clientSecret":223})
#         # da_shop.create()
#         print(da_shop.clientId)
#         # RequestHandler(da_shop).refreshToken()


class ShipmentTestCase(TestCase):
    # Create your tests here.
    def test_update_shipment(self):
        url = "http://127.0.0.1:8000/update_shipment"

        payload = '{\r\n    "shop_name":["boloo"]\r\n}'
        headers = {"Content-Type": "application/json"}

        response = requests.request("POST", url, headers=headers, data=payload)
        assert str(response.text) == '200'

    # def test_repeat_1000_shiment(self):
    #     url = "http://127.0.0.1:8000/update_shipment"

    #     many_bolo = str(["boloo" for i in range(200001)])
    #     tmp_payload = {"shop_name": many_bolo}
    #     payload = json.dumps(tmp_payload)
    #     headers = {"Content-Type": "application/json"}

    #     response = requests.request("POST", url, headers=headers, data=payload)
    #     assert str(response.text) == '200'

