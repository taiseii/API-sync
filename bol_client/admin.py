from django.contrib import admin
from .models import (ShopCredentials, Shipments, ShipmentsItems, Transport,
                     CustomerDetails, shopRequestLog, tokenRequestLog)

admin.site.register(ShopCredentials)
admin.site.register(Shipments)
admin.site.register(ShipmentsItems)
admin.site.register(Transport)
admin.site.register(CustomerDetails)
admin.site.register(shopRequestLog)
admin.site.register(tokenRequestLog)