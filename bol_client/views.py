from .tasks import initialiseShipmentSync
import requests
import json
from base64 import b64encode
from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from rest_framework import status
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
    shopRequestLog,
    tokenRequestLog,
)
from .serializers import (
    ShopCredentialsSerializer,
    ShipmentsSerializer,
    ShipmentsItemsSerializer,
    TransportSerializer,
    CustomerDetailsSerializer,
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


class tokenRequestLogSerializerView(viewsets.ModelViewSet):
    queryset = tokenRequestLog.objects.all()
    serializer_class = shopRequestLogSerializer


class shopRequestLogSerializerView(viewsets.ModelViewSet):
    queryset = shopRequestLog.objects.all()
    serializer_class = shopRequestLogSerializer


class UpdateShipmentView(APIView):
    """
    Where execution of the sync happens
    """

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
                    "shipmentId": 780184287,
                    "shipmentDate": "2020-08-20T19:49:22+02:00",
                    "shipmentReference": "P2020-10533",
                    "shipmentItems": [
                        {
                            "orderItemId": "2443071085",
                            "orderId": "1135670078"
                        }
                    ],
                    "transport": {
                        "transportId": 521249417
                    }
                },
                {
                    "shipmentId": 777298069,
                    "shipmentDate": "2020-08-11T17:12:19+02:00",
                    "shipmentReference": "P2020-9451",
                    "shipmentItems": [
                        {
                            "orderItemId": "2439306307",
                            "orderId": "1133440117"
                        }
                    ],
                    "transport": {
                        "transportId": 518251373
                    }
                },
                {
                    "shipmentId": 773780130,
                    "shipmentDate": "2020-07-31T17:19:25+02:00",
                    "shipmentReference": "P2020-7742",
                    "shipmentItems": [
                        {
                            "orderItemId": "2434918422",
                            "orderId": "1130406498"
                        }
                    ],
                    "transport": {
                        "transportId": 514639454
                    }
                },
                {
                    "shipmentId": 773780126,
                    "shipmentDate": "2020-07-31T17:19:22+02:00",
                    "shipmentReference": "P2020-7743",
                    "shipmentItems": [
                        {
                            "orderItemId": "2434924939",
                            "orderId": "1130410755"
                        }
                    ],
                    "transport": {
                        "transportId": 514639448
                    }
                },
                {
                    "shipmentId": 773397055,
                    "shipmentDate": "2020-07-30T15:05:05+02:00",
                    "shipmentItems": [
                        {
                            "orderItemId": "2430476244",
                            "orderId": "1128667641"
                        }
                    ],
                    "transport": {
                        "transportId": 514245508
                    }
                },
                {
                    "shipmentId": 773293313,
                    "shipmentDate": "2020-07-30T10:04:22+02:00",
                    "shipmentReference": "P2020-7602",
                    "shipmentItems": [
                        {
                            "orderItemId": "2434618878",
                            "orderId": "1130198146"
                        }
                    ],
                    "transport": {
                        "transportId": 514136952
                    }
                }
            ]
        }
        test_shipment_obj_2 = {
            "shipments": [
                {
                    "shipmentId": 780184299,
                    "shipmentDate": "2020-08-20T19:49:22+02:00",
                    "shipmentReference": "P2020-10533",
                    "shipmentItems": [
                        {
                            "orderItemId": "2443071085",
                            "orderId": "1135670078"
                        }
                    ],
                    "transport": {
                        "transportId": 521249417
                    }
                },
                {
                    "shipmentId": 777245069,
                    "shipmentDate": "2020-08-11T17:12:19+02:00",
                    "shipmentReference": "P2020-9451",
                    "shipmentItems": [
                        {
                            "orderItemId": "2439306307",
                            "orderId": "1133440117"
                        }
                    ],
                    "transport": {
                        "transportId": 518251373
                    }
                },
                {
                    "shipmentId": 733080130,
                    "shipmentDate": "2020-07-31T17:19:25+02:00",
                    "shipmentReference": "P2020-7742",
                    "shipmentItems": [
                        {
                            "orderItemId": "2434918422",
                            "orderId": "1130406498"
                        }
                    ],
                    "transport": {
                        "transportId": 514639454
                    }
                }
            ]
        }
        test_shipment_obj_3 = {}
        test_shipment_obj = [
            test_shipment_obj_1,
            test_shipment_obj_2,
            test_shipment_obj_3,
        ]

    return Response(test_shipment_obj[int(page) - 1], status=status.HTTP_200_OK)


@api_view(["GET"])
def test_get_shipment_detail(request, pk):
    if request.method == "GET":

        shipment_id_list = [777298069, 773780130, 773780126, 773397055,
                            773293313, 780184299, 777245069, 733080130,
                            780184287]
        all_test_shipment_detail_obj = {i: {
            "shipmentId": i,
            "pickUpPoint": 'false',
            "shipmentDate": "2020-08-20T19:49:22+02:00",
            "shipmentReference": "P2020-10533",
            "shipmentItems": [
                {
                    "orderItemId": "2443071085",
                    "orderId": "1135670078",
                    "orderDate": "2020-08-20T15:50:54+02:00",
                    "latestDeliveryDate": "2020-08-24T00:00:00+02:00",
                    "ean": "7141225472340",
                    "title": "Desinfecterende Handgel - Handgel Desinfecterende - 250 ml - Desinfectie - Desinfecterende Alcohol Spray - Desinfecterende Handspray - Handig Meenemen",
                    "quantity": 4,
                    "offerPrice": 59.80,
                    "offerCondition": "UNKNOWN",
                    "fulfilmentMethod": "FBR"
                }
            ],
            "transport": {
                "transportId": 521249417,
                "transporterCode": "TNT",
                "trackAndTrace": "3SYZXG127962494"
            },
            "customerDetails": {
                "salutationCode": "03",
                "zipCode": "1213PB",
                "countryCode": "NL"
            }
        } for i in shipment_id_list
        }

        print(all_test_shipment_detail_obj[pk])

        return Response(all_test_shipment_detail_obj[pk], status=status.HTTP_200_OK)
