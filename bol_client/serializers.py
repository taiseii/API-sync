from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from cryptography.fernet import Fernet
from django.conf import settings
from .models import (ShopCredentials, Shipments, ShipmentsItems,
                     Transport, CustomerDetails, shopRequestLog,
                     tokenRequestLog)


class ShopCredentialsSerializer(serializers.ModelSerializer):

    def _encrypt(self, clientSecret):
        return Fernet(settings.SHOP_KEY).encrypt(bytes(clientSecret, 'utf-8'))

    def create(self, validated_data):
        new_validated_data = {
            "shopName": validated_data['shopName'],
            "clientId": validated_data['clientId'],
            "clientSecret": self._encrypt(validated_data['clientSecret'])
        }
        return super().create(new_validated_data)

    class Meta:
        model = ShopCredentials
        fields = ('shopId', 'shopName', 'clientId',
                  'clientSecret', 'clientToken')


class ShipmentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shipments
        fields = ('shipmentId', 'shipmentDate', 'shipmentReference',
                  'transportId', 'shopId', 'orderItemId', 'orderId')


class ShipmentsItemsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShipmentsItems
        fields = ('pickUpPoint', 'orderItemId', 'orderId', 'orderDate',
                  'latestDeliveryDate', 'ean', 'title', 'quantity', 'offerPrice',
                  'offerCondition', 'offerReference', 'fulfilmentMethod',
                  'shipmentId')


class TransportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transport
        fields = ('transportId', 'transporterCode', 'trackAndTrace',
                  'shipmentId')


class CustomerDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerDetails
        fields = ('salutationCode', 'zipCode', 'countryCode', 'shipmentId')


class tokenRequestLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = tokenRequestLog
        fields = ('taskId', 'completed', 'shopId')


class shopRequestLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = shopRequestLog
        fields = ('taskId', 'completed', 'shopId')
