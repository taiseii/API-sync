import requests
import json
from base64 import b64encode
from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import (
    ShopCredentials,
    Shipments,
    ShipmentsItems,
    Transport,
    CustomerDetails,
    BillingDetails,
    shopRequestLog,
    tokenRequestLog,
)
from .serializers import (
    ShopCredentialsSerializer,
    ShipmentsSerializer,
    ShipmentsItemsSerializer,
    TransportSerializer,
    CustomerDetailsSerializer,
    BillingDetailsSerializer,
    shopRequestLogSerializer,
    tokenRequestLogSerializer,
)
from boloo_api.celery import app as celery_app
from _thread import start_new_thread
from concurrent.futures import ThreadPoolExecutor


class ShopCredentialsView(viewsets.ModelViewSet):
    queryset = ShopCredentials.objects.all()
    serializer_class = ShopCredentialsSerializer


class ShipmentsView(viewsets.ModelViewSet):
    queryset = Shipments.objects.all()
    serializer_class = ShipmentsSerializer


class ShipmentsItemsView(viewsets.ModelViewSet):
    queryset = ShipmentsItems.objects.all()
    serializer_class = ShipmentsItemsSerializer


class TransportSerializerView(viewsets.ModelViewSet):
    queryset = Transport.objects.all()
    serializer_class = TransportSerializer


class CustomerDetailsSerializerView(viewsets.ModelViewSet):
    queryset = CustomerDetails.objects.all()
    serializer_class = CustomerDetailsSerializer


class BillingDetailsSerializerView(viewsets.ModelViewSet):
    queryset = BillingDetails.objects.all()
    serializer_class = BillingDetailsSerializer


class tokenRequestLogSerializerView(viewsets.ModelViewSet):
    queryset = tokenRequestLog.objects.all()
    serializer_class = shopRequestLogSerializer


class shopRequestLogSerializerView(viewsets.ModelViewSet):
    queryset = shopRequestLog.objects.all()
    serializer_class = shopRequestLogSerializer

from .tasks import initialiseShipmentSync


class UpdateShipmentView(APIView):

    parser_class = [JSONParser]

    def syncShipments(self, shopName):
        initialiseShipmentSync.delay(shopName)

    def post(self, request):
        with ThreadPoolExecutor(max_workers=20) as executor:
            for shopName in eval(str(request.data["shop_name"])):
                executor.submit(self.syncShipments, shopName)

        return HttpResponse(200)


@api_view(["GET"])
def test_get_shipment(request, page):
    if request.method == "GET":
        page = request.query_params.get("page")
        print(f"page:{page}")
        test_shipment_obj_1 = {
            "shipments": [
                {
                    "shipmentId": 541757635,
                    "shipmentDate": "2018-04-17T10:55:37+02:00",
                    "shipmentReference": "BOLCOM001",
                    "shipmentItems": [
                        {"orderItemId": "1234567891", "orderId": "4123456789"}
                    ],
                    "transport": {"transportId": 312778947},
                },
                {
                    "shipmentId": 541757636,
                    "shipmentDate": "2018-05-17T10:55:37+02:00",
                    "shipmentReference": "BOLCOM002",
                    "shipmentItems": [
                        {"orderItemId": "1234567892", "orderId": "4123456790"}
                    ],
                    "transport": {"transportId": 312778948},
                },
            ]
        }
        test_shipment_obj_2 = {
            # "shipments": [
            #     {
            #         "shipmentId": 541757637,
            #         "shipmentDate": "2018-04-18T10:55:39+02:00",
            #         "shipmentReference": "BOLCOM001",
            #         "shipmentItems": [
            #             {"orderItemId": "1234567891", "orderId": "4123456789"}
            #         ],
            #         "transport": {"transportId": 312778947},
            #     },
            #     {
            #         "shipmentId": 541757638,
            #         "shipmentDate": "2018-05-17T10:55:37+02:00",
            #         "shipmentReference": "BOLCOM002",
            #         "shipmentItems": [
            #             {"orderItemId": "1234567892", "orderId": "4123456790"}
            #         ],
            #         "transport": {"transportId": 312778948},
            #     },
            # ]
        }
        test_shipment_obj_3 = {}
        test_shipment_obj = [
            test_shipment_obj_1,
            test_shipment_obj_2,
            test_shipment_obj_3,
        ]

    return Response(test_shipment_obj[int(page) - 1])


@api_view(["GET"])
def test_get_shipment_detail(request, pk):
    if request.method == "GET":
        all_test_shipment_detail_obj = [
            {
                "shipmentId": 541757635,
                "pickUpPoint": "true",
                "shipmentDate": "2018-04-17T10:55:37+02:00",
                "shipmentReference": "BOLCOM001",
                "shipmentItems": [
                    {
                        "orderItemId": "1234567891",
                        "orderId": "4123456789",
                        "orderDate": "2018-04-17T10:55:37+02:00",
                        "latestDeliveryDate": "2018-04-20T10:55:37+02:00",
                        "ean": "0000007740404",
                        "title": "Product Title",
                        "quantity": 10,
                        "offerPrice": 12.99,
                        "offerCondition": "NEW",
                        "offerReference": "BOLCOM00123",
                        "fulfilmentMethod": "FBR",
                    },
                    {
                        "orderItemId": "1234567892",
                        "orderId": "4123456789",
                        "orderDate": "2018-04-17T10:55:37+02:00",
                        "latestDeliveryDate": "2018-04-20T10:55:37+02:00",
                        "ean": "0000007740404",
                        "title": "Product Title",
                        "quantity": 10,
                        "offerPrice": 12.99,
                        "offerCondition": "NEW",
                        "offerReference": "BOLCOM00124",
                        "fulfilmentMethod": "FBR",
                    },
                ],
                "transport": {
                    "transportId": 312778947,
                    "transporterCode": "TNT",
                    "trackAndTrace": "3SBOL0987654321",
                    "shippingLabelId": 123456789,
                    "shippingLabelCode": "PLR00000002",
                },
                "customerDetails": {
                    "pickUpPointName": "Albert Heijn: UTRECHT",
                    "salutationCode": "02",
                    "firstName": "Billie",
                    "surname": "Jansen",
                    "streetName": "Dorpstraat",
                    "houseNumber": "1",
                    "houseNumberExtended": "B",
                    "addressSupplement": "Afdeling kwaliteit",
                    "extraAddressInformation": "Apartment",
                    "zipCode": "1111 ZZ",
                    "city": "Utrecht",
                    "countryCode": "NL",
                    "email": "billie@verkopen.bol.com",
                    "company": "bol.com",
                    "vatNumber": "NL999999999B99",
                    "chamberOfCommerceNumber": "99887766",
                    "orderReference": "MijnReferentie",
                    "deliveryPhoneNumber": "012123456",
                },
                "billingDetails": {
                    "pickUpPointName": "Albert Heijn: UTRECHT",
                    "salutationCode": "02",
                    "firstName": "Billie",
                    "surname": "Jansen",
                    "streetName": "Dorpstraat",
                    "houseNumber": "1",
                    "houseNumberExtended": "B",
                    "addressSupplement": "Afdeling kwaliteit",
                    "extraAddressInformation": "Apartment",
                    "zipCode": "1111 ZZ",
                    "city": "Utrecht",
                    "countryCode": "NL",
                    "email": "billie@verkopen.bol.com",
                    "company": "bol.com",
                    "vatNumber": "NL999999999B99",
                    "chamberOfCommerceNumber": "99887766",
                    "orderReference": "MijnReferentie",
                    "deliveryPhoneNumber": "012123456",
                },
            },
            {
                "shipmentId": 541757636,
                "pickUpPoint": "true",
                "shipmentDate": "2018-04-17T10:55:37+02:00",
                "shipmentReference": "BOLCOM001",
                "shipmentItems": [
                    {
                        "orderItemId": "1234567891",
                        "orderId": "4123456789",
                        "orderDate": "2018-04-17T10:55:37+02:00",
                        "latestDeliveryDate": "2018-04-20T10:55:37+02:00",
                        "ean": "0000007740404",
                        "title": "Product Title",
                        "quantity": 10,
                        "offerPrice": 12.99,
                        "offerCondition": "NEW",
                        "offerReference": "BOLCOM00123",
                        "fulfilmentMethod": "FBR",
                    }
                ],
                "transport": {
                    "transportId": 312778947,
                    "transporterCode": "TNT",
                    "trackAndTrace": "3SBOL0987654321",
                    "shippingLabelId": 123456789,
                    "shippingLabelCode": "PLR00000002",
                },
                "customerDetails": {
                    "pickUpPointName": "Albert Heijn: UTRECHT",
                    "salutationCode": "02",
                    "firstName": "Billie",
                    "surname": "Jansen",
                    "streetName": "Dorpstraat",
                    "houseNumber": "1",
                    "houseNumberExtended": "B",
                    "addressSupplement": "Afdeling kwaliteit",
                    "extraAddressInformation": "Apartment",
                    "zipCode": "1111 ZZ",
                    "city": "Utrecht",
                    "countryCode": "NL",
                    "email": "billie@verkopen.bol.com",
                    "company": "bol.com",
                    "vatNumber": "NL999999999B99",
                    "chamberOfCommerceNumber": "99887766",
                    "orderReference": "MijnReferentie",
                    "deliveryPhoneNumber": "012123456",
                },
                "billingDetails": {
                    "pickUpPointName": "Albert Heijn: UTRECHT",
                    "salutationCode": "02",
                    "firstName": "Billie",
                    "surname": "Jansen",
                    "streetName": "Dorpstraat",
                    "houseNumber": "1",
                    "houseNumberExtended": "B",
                    "addressSupplement": "Afdeling kwaliteit",
                    "extraAddressInformation": "Apartment",
                    "zipCode": "1111 ZZ",
                    "city": "Utrecht",
                    "countryCode": "NL",
                    "email": "billie@verkopen.bol.com",
                    "company": "bol.com",
                    "vatNumber": "NL999999999B99",
                    "chamberOfCommerceNumber": "99887766",
                    "orderReference": "MijnReferentie",
                    "deliveryPhoneNumber": "012123456",
                },
            },
        ]

        for i in all_test_shipment_detail_obj:
            if pk == i["shipmentId"]:
                return Response(i)

        return Response(all_test_shipment_detail_obj)
