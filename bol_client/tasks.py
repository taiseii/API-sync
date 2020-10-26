import json
import requests
from datetime import datetime, timezone, timedelta
import maya
from base64 import b64encode
from celery import shared_task, Task
from time import sleep
from rest_framework import status
from django.http import HttpResponse
from django.conf import settings
from rest_framework.response import Response
from cryptography.fernet import Fernet
from .models import (
    ShopCredentials,
    tokenRequestLog,
    shopRequestLog,
    Shipments,
    Transport,
    CustomerDetails,
    BillingDetails,
)
from .serializers import (
    ShopCredentialsSerializer,
    tokenRequestLogSerializer,
    shopRequestLogSerializer,
    ShipmentsSerializer,
    ShipmentsItemsSerializer,
    TransportSerializer,
    CustomerDetailsSerializer,
    BillingDetailsSerializer,
)


class RequestHandler(Task):
    """
    request handler class
    where actual request to the bol API is being perfomed.
    This class contains all the methods used to call request
    to bol API.

    Args:
        shop {ShopCredentials}: shop credentials object
        rateLimitHandler {RateLimitHandler}: rate limit handler
            class dedicated to prevent overshooting of API call
    """

    def __init__(self, shop):
        self.shop = shop
        self.rateLimitHandler = RateLimitHandler(shop)

    def sendRequest(self, url):
        """
        This funtion will send the request to bol API

        Args:
            self:
            url {str}: url which we want to send request

        Return:
            body of the request converted to
            dictionary pythyon object
        """
        sleep(self.rateLimitHandler.waitCall())
        if settings.DEBUG:
            headers = {"Accept": "*/*"}
        else:
            headers = {
                "Accept": "application/vnd.retailer.v3+json",
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.shop.clientToken}",
            }

        payload = {}
        response = requests.request("GET", url, headers=headers, data=payload)
        self.rateLimitHandler.saveRequestLog()
        return eval(response.text)

    def decrypt(self):
        return Fernet(settings.SHOP_KEY).decrypt(eval(self.shop.clientSecret))

    def refreshToken(self):

        """
        refresh bearer token of the shop when needed

        Args:
            self

        Returns:
            {list} of shop object and bearer token
        """
        url = "https://login.bol.com/token?grant_type=client_credentials"
        payload = {}
        print(f'decrypted : { str(self.decrypt()) }')
        print('refresh token')
        credentials = f"{self.shop.clientId}:{self.decrypt().decode('utf-8')}"
        encodedCredentials = str(b64encode(credentials.encode("utf-8")), "utf-8")
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Basic {encodedCredentials}",
        }

        try:
            if settings.DEBUG:
                data = {"clientToken": "testaa"}
            else:
                response = requests.request("POST", url, headers=headers, data=payload)
                print(headers)
                print(json.loads(response.text.encode("utf-8")))
                data = {
                    "clientToken": json.loads(response.text.encode("utf8"))[
                        "access_token"
                    ]
                }
        except Exception as e:
            raise Exception(e)

        self.rateLimitHandler.saveTokenLog()
        serializer = ShopCredentialsSerializer(self.shop, data)
        if serializer.is_valid():
            serializer.save()
            return True
        else:
            raise Exception(serializer.errors)

        return self.shop, data

    def syncShipment(self):
        """
        execute GET request to bol API to sync overview
        Call method from ShipmentOverviewHandler and ShipmentDetailHandler
        to save all the necessary data.
        This method will only save those shipment data which does not
        already exist in the db to save space.
        This method will execute API call to /shipement/{shipment-id}

        Args:
            self

        Return:
            None
        """
        page_obj = {"start"}
        counter = 1
        firfilment_list = ["FBR", "FBB"]
        for fm in firfilment_list:
            while page_obj:

                if settings.DEBUG:
                    url = f"http://127.0.0.1:8000/test_get_shipment/?page={counter}"
                else:
                    url = f"https://api.bol.com/retailer/shipments?page={counter}?filfilment-method={fm}"

                page_obj = self.sendRequest(url)
                self.rateLimitHandler.saveRequestLog()
                shipmentIdList = ShipmentOverviewHandler(
                    self.shop, data=page_obj
                ).saveShipment()

                if shipmentIdList:
                    for ship_id in shipmentIdList:
                        self.syncShipmentDetails(ship_id)

                if counter == 10:
                    print(page_obj)
                    print(shipmentIdList)
                    break

                counter += 1

    def syncShipmentDetails(self, shipmentId: int):
        """
        call to /shipmnts/sipmentsId after syncShipment has been executed.
        Because syncShipment have to be called first so that we know
        the target shipmentId.

        Args:
            shipmentId {int}: shipmentId from syncShipment

        Returns:
            Response object with called detail_shipment object
        """
        if settings.DEBUG:
            url = f"http://127.0.0.1:8000/test_get_shipment_detail/{shipmentId}"
        else:
            url = f"https://api.bol.com/retailer/shipments/{shipmentId}"

        detail_obj = self.sendRequest(url)
        ShipmentDetailHandler(self.shop, shipmentId, detail_obj).saveAll()
        return Response(detail_obj, status=status.HTTP_201_CREATED)


class RateLimitHandler(Task):
    """
    class handling rate limiting of the API call
    per shop. When the token is request or call
    is made to the bol route, these activity will be
    logged at tokenRequestLog and shopRequestLog table

    Args:
        shop {ShopCredentials}: ShopCredentialsObject
    """

    def __init__(self, shop):
        self.shop = shop

    def waitCall(self):
        """
        Query the log in respect to current time - 1hr.
        If the count of this is larger than 200000
        else wait 1 hr

        Args:
            self
        Returns:
            0 if we haven't reached the limit yet.
            1hr if we reached the limit already
        """
        from_when = datetime.now(timezone.utc) - timedelta(seconds=settings.TOTAL_CYCLE)
        calls_made = shopRequestLog.objects.filter(
            completed__gt=from_when, shopId=self.shop.shopId
        )
        remaining_call = settings.TOTAL_CALL_PER_CYCLE - len(calls_made)
        if remaining_call <= 0:
            return settings.TOTAL_CYCLE
        else:
            return 0

    def saveTokenLog(self):
        """
        save shop info and time stamp of when
        the token has been requested

        Args:
            self
        Return:
            True {bool}
        """
        serializer = tokenRequestLogSerializer(data={"shopId": self.shop.shopId})

        if serializer.is_valid():
            serializer.save()
            print("token request log is saved")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Exception(serializer.errors)

        return True

    def saveRequestLog(self):
        """
        save shop info and time stamp of when
        the api call has been requested

        Args:
            self
        Return:
            True {bool}
        """
        serializer = shopRequestLogSerializer(data={"shopId": self.shop.shopId})

        if serializer.is_valid():
            serializer.save()
            print(" request log is saved")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            raise Exception(serializer.errors)

        return True


class ShipmentOverviewHandler(Task):
    def __init__(self, shop, data):
        self.shop = shop
        self.data = data

    def saveShipment(self):
        """
        sync to the Shipments table.
        This function will lookup what
        shipomentId has alraedy been saved
        in the db and save only the new item

        Args:
            self
        Return:
            shipment_id_list{list}: list of shipmentId which
                does not exist in the database
        """
        shipment_id_list = []
        try:
            if self.data:
                print(self.data)
                for shipment in self.data["shipments"]:
                    shipment_obj = Shipments.objects.filter(
                        shipmentId=shipment["shipmentId"]
                    )
                    if len(shipment_obj) == 0:
                        # save new shipment to db
                        date_time_obj = maya.parse(shipment["shipmentDate"]).datetime()
                        data = {
                            "shipmentId": shipment["shipmentId"],
                            "shipmentDate": date_time_obj,
                            "shipmentReference": shipment["shipmentReference"],
                            "transportId": shipment["transport"]["transportId"],
                            "shopId": self.shop.shopId,
                        }
                        serializer = ShipmentsSerializer(data=data)
                        if serializer.is_valid():
                            print("valid")
                            serializer.save()
                            shipment_id_list.append(shipment["shipmentId"])
                        else:
                            raise Exception(serializer.errors)
                return shipment_id_list
        except Exception as e:
            print(e)

class ShipmentDetailHandler(Task):
    """
    this class saved the detailed shipment
    information to appropriate table.

    Args:
        shop {shopCredential}:
        data {dictionary}: return of the shipment/{shipment_id}
        shipmentId {int}: detaild shipment information of
                            shipmentId
    """

    def __init__(self, shop, shipmentId, data):
        self.shop = shop
        self.data = data
        self.shipmentId = shipmentId

    def saveAll(self):
        self.saveShipmentItems()
        self.saveTransport()
        self.saveCustomerDetails()
        self.saveBillingDetails()

    def saveShipmentItems(self):
        for shipmentItem in self.data["shipmentItems"]:

            print(f"shipment Item {shipmentItem}")

            # maya.parse(shipment["shipmentDate"]).datetime()

            data = {
                "orderItemId": shipmentItem["orderItemId"],
                "orderId": shipmentItem["orderId"],
                "orderDate": maya.parse(shipmentItem["orderDate"]).datetime(),
                "latestDeliveryDate": maya.parse(
                    shipmentItem["latestDeliveryDate"]
                ).datetime(),
                "ean": shipmentItem["ean"],
                "title": shipmentItem["title"],
                "quantity": shipmentItem["quantity"],
                "offerprice": shipmentItem["offerPrice"],
                "offerCondition": shipmentItem["offerCondition"],
                "offerReference": shipmentItem["offerReference"],
                "fulfilmentMethod": shipmentItem["fulfilmentMethod"],
                "shipmentId": self.shipmentId,
            }
            serializer = ShipmentsItemsSerializer(data=data)

            if serializer.is_valid():
                serializer.save()
                print("shipment detail saved")
            else:
                raise Exception(serializer.errors)

        return True

    def saveTransport(self):
        # print(transport)
        transport = self.data["transport"]
        data = {
            "transportId": transport["transportId"],
            "transporterCode": transport["transporterCode"],
            "trackAndTrace": transport["trackAndTrace"],
            "shippingLabelId": transport["shippingLabelId"],
            "shippingLabelCode": transport["shippingLabelCode"],
            "shipmentId": self.shipmentId,
        }
        serializer = TransportSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            print("transport detail is saved")
        else:
            raise Exception(serializer.errors)

        return True

    def saveCustomerDetails(self):
        customer_detail = self.data["customerDetails"]
        data = {
            "pickUpPointName": customer_detail["pickUpPointName"],
            "salutationCode": customer_detail["salutationCode"],
            "firstName": customer_detail["firstName"],
            "surname": customer_detail["surname"],
            "streetName": customer_detail["streetName"],
            "houseNumber": customer_detail["houseNumber"],
            "houseNumberExtended": customer_detail["houseNumberExtended"],
            "addressSupplement": customer_detail["addressSupplement"],
            "extraAddressInformation": customer_detail["extraAddressInformation"],
            "zipCode": customer_detail["zipCode"],
            "city": customer_detail["city"],
            "countryCode": customer_detail["countryCode"],
            "email": customer_detail["email"],
            "company": customer_detail["company"],
            "vatNumber": customer_detail["vatNumber"],
            "chamberOfCommerceNumber": customer_detail["chamberOfCommerceNumber"],
            "orderReference": customer_detail["orderReference"],
            "deliveryPhoneNumber": customer_detail["deliveryPhoneNumber"],
            "shipmentId": self.shipmentId,
        }
        serializer = CustomerDetailsSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            print("customer detail is saved")
        else:
            raise Exception(serializer.errors)

        return True

    def saveBillingDetails(self):
        billing_detail = self.data["billingDetails"]
        data = {
            "pickUpPointName": billing_detail["pickUpPointName"],
            "salutationCode": billing_detail["salutationCode"],
            "firstName": billing_detail["firstName"],
            "surname": billing_detail["surname"],
            "streetName": billing_detail["streetName"],
            "houseNumber": billing_detail["houseNumber"],
            "houseNumberExtended": billing_detail["houseNumberExtended"],
            "addressSupplement": billing_detail["addressSupplement"],
            "extraAddressInformation": billing_detail["extraAddressInformation"],
            "zipCode": billing_detail["zipCode"],
            "city": billing_detail["city"],
            "countryCode": billing_detail["countryCode"],
            "email": billing_detail["email"],
            "company": billing_detail["company"],
            "vatNumber": billing_detail["vatNumber"],
            "chamberOfCommerceNumber": billing_detail["chamberOfCommerceNumber"],
            "orderReference": billing_detail["orderReference"],
            "deliveryPhoneNumber": billing_detail["deliveryPhoneNumber"],
            "shipmentId": self.shipmentId,
        }
        serializer = BillingDetailsSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            print("billing detail is saved")
        else:
            raise Exception(serializer.errors)

        return True


@shared_task
def initialiseShipmentSync(shopName):
    """
    initialize Shipment Sync process.
    This is the logic used to initialize the
    all the sync process by evaluating status
    of the token and the shipment request.

    Args:
        shopName {str}: name of the shop

    """
    try:
        da_shop = ShopCredentials.objects.filter(shopName=shopName)[0]
    except Exception:
        raise Exception("Shop does not exist")

    requestsHandler = RequestHandler(da_shop)

    if da_shop.clientToken == "":
        requestsHandler.refreshToken()
        requestsHandler.syncShipment()
    else:
        tokenLog = tokenRequestLog.objects.filter(shopId=da_shop.shopId).order_by(
            "-taskId"
        )[0]
        delta_time = datetime.now(timezone.utc) - tokenLog.completed
        if delta_time.seconds > settings.TOKEN_DURATION:
            print("need to update bearer token")
            requestsHandler.refreshToken()
            requestsHandler.syncShipment()
        else:
            print("need to reuse the token")
            requestsHandler.syncShipment()
