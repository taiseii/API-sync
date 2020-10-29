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
    shipmentReference = models.CharField(max_length=50, default='')
    transportId = models.IntegerField()
    orderItemId = models.CharField(max_length=50, default='')
    orderId = models.CharField(max_length=50, default='')
    shopId = models.ForeignKey(ShopCredentials, on_delete=models.CASCADE)


class ShipmentsItems(models.Model):
    pickUpPoint = models.CharField(max_length=50, default='')
    orderItemId = models.IntegerField()
    orderId = models.IntegerField()
    orderDate = models.DateTimeField()
    latestDeliveryDate = models.DateTimeField()
    ean = models.CharField(max_length=100, default='')
    title = models.CharField(max_length=1000, default='')
    quantity = models.IntegerField()
    offerPrice = models.FloatField()
    offerCondition = models.CharField(max_length=50, default='')
    offerReference = models.CharField(max_length=50, default='')
    fulfilmentMethod = models.CharField(max_length=50, default='')
    shipmentId = models.ForeignKey(Shipments, on_delete=models.CASCADE)


class Transport(models.Model):
    transportId = models.IntegerField()
    transporterCode = models.CharField(max_length=50, default='')
    trackAndTrace = models.CharField(max_length=50, default='')
    shipmentId = models.ForeignKey(Shipments, on_delete=models.CASCADE)


class CustomerDetails(models.Model):
    salutationCode = models.CharField(max_length=50, default='')
    zipCode = models.CharField(max_length=50, default='')
    countryCode = models.CharField(max_length=50, default='')
    shipmentId = models.ForeignKey(Shipments, on_delete=models.CASCADE)


class tokenRequestLog(models.Model):
    taskId = models.AutoField(primary_key=True)
    completed = models.DateTimeField(auto_now=True)
    shopId = models.ForeignKey(ShopCredentials, on_delete=models.CASCADE)


class shopRequestLog(models.Model):
    taskId = models.AutoField(primary_key=True)
    completed = models.DateTimeField(auto_now=True)
    shopId = models.ForeignKey(ShopCredentials, on_delete=models.CASCADE)
