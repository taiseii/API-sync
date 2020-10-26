from django.db import models


class ShopCredentials(models.Model):
    shopName = models.CharField(max_length=50, default='', unique=True)
    shopId = models.AutoField(primary_key=True)
    clientId = models.CharField(max_length=50, default='', unique=True)
    clientSecret = models.CharField(max_length=100, default='')
    clientToken = models.CharField(max_length=1000, default='')


class Shipments(models.Model):
    shipmentId = models.IntegerField(primary_key=True)
    shipmentDate = models.DateTimeField()
    shipmentReference = models.CharField(max_length=50)
    transportId = models.IntegerField()
    shopId = models.ForeignKey(ShopCredentials, on_delete=models.CASCADE)


class ShipmentsItems(models.Model):
    orderItemId = models.IntegerField()
    orderId = models.IntegerField()
    orderDate = models.DateTimeField()
    latestDeliveryDate = models.DateTimeField()
    ean = models.IntegerField()
    title = models.CharField(max_length=50, default='')
    quantity = models.IntegerField()
    offerprice = models.FloatField()
    offerCondition = models.CharField(max_length=50, default='')
    offerReference = models.CharField(max_length=50, default='')
    fulfilmentMethod = models.CharField(max_length=50, default='')
    shipmentId = models.ForeignKey(Shipments, on_delete=models.CASCADE)


class Transport(models.Model):
    transportId = models.IntegerField()
    transporterCode = models.CharField(max_length=50, default='')
    trackAndTrace = models.CharField(max_length=50, default='')
    shippingLabelId = models.IntegerField()
    shippingLabelCode = models.CharField(max_length=50, default='')
    shipmentId = models.ForeignKey(Shipments, on_delete=models.CASCADE)


class CustomerDetails(models.Model):
    pickUpPointName = models.CharField(max_length=50, default='')
    salutationCode = models.CharField(max_length=50, default='')
    firstName = models.CharField(max_length=50, default='')
    surname = models.CharField(max_length=50, default='')
    streetName = models.CharField(max_length=50, default='')
    houseNumber = models.CharField(max_length=50, default='')
    houseNumberExtended = models.CharField(max_length=50, default='')
    addressSupplement = models.CharField(max_length=50, default='')
    extraAddressInformation = models.CharField(max_length=50, default='')
    zipCode = models.CharField(max_length=50, default='')
    city = models.CharField(max_length=50, default='')
    countryCode = models.CharField(max_length=50, default='')
    email = models.CharField(max_length=50, default='')
    company = models.CharField(max_length=50, default='')
    vatNumber = models.CharField(max_length=50, default='')
    chamberOfCommerceNumber = models.CharField(max_length=50, default='')
    orderReference = models.CharField(max_length=50, default='')
    deliveryPhoneNumber = models.CharField(max_length=50, default='')
    shipmentId = models.ForeignKey(Shipments, on_delete=models.CASCADE)


class BillingDetails(models.Model):
    pickUpPointName = models.CharField(max_length=50, default='')
    salutationCode = models.CharField(max_length=50, default='')
    firstName = models.CharField(max_length=50, default='')
    surname = models.CharField(max_length=50, default='')
    streetName = models.CharField(max_length=50, default='')
    houseNumber = models.CharField(max_length=50, default='')
    houseNumberExtended = models.CharField(max_length=50, default='')
    addressSupplement = models.CharField(max_length=50, default='')
    extraAddressInformation = models.CharField(max_length=50, default='')
    zipCode = models.CharField(max_length=50, default='')
    city = models.CharField(max_length=50, default='')
    countryCode = models.CharField(max_length=50, default='')
    email = models.CharField(max_length=50, default='')
    company = models.CharField(max_length=50, default='')
    vatNumber = models.CharField(max_length=50, default='')
    chamberOfCommerceNumber = models.CharField(max_length=50, default='')
    orderReference = models.CharField(max_length=50, default='')
    deliveryPhoneNumber = models.CharField(max_length=50, default='')
    shipmentId = models.ForeignKey(Shipments, on_delete=models.CASCADE)


class tokenRequestLog(models.Model):
    taskId = models.AutoField(primary_key=True)
    completed = models.DateTimeField(auto_now=True)
    shopId = models.ForeignKey(ShopCredentials, on_delete=models.CASCADE)


class shopRequestLog(models.Model):
    taskId = models.AutoField(primary_key=True)
    completed = models.DateTimeField(auto_now=True)
    shopId = models.ForeignKey(ShopCredentials, on_delete=models.CASCADE)
