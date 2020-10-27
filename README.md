# 📡 API-sync

Sync API data to database

### 🛠️ Setup + Prerequsite
- setup RabbitMQ in local macine or cloud
```sh
sudo service rabbitmq-server start
```
- setup MySQL in local machine or cloud

```sh
git clone https://github.com/taiseii/API-sync.git
cd API-syncs
pipenv install -r requirements.txt
```
edit setting file in `API-sync/boloo_api/settings.py`
```py
SECRET_KEY = "secret secret secret"
SHOP_KEY = "secret secret"
```
celery setting, if running RabbitMQ locally
```
CELERY_BROKER_URL = 'amqp://127.0.0.1:5672/'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
```
RabbitMQ and MySQL setup...

### 🍭 Gettings Started
migrate + runserver
```py
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```
Start celery in the virutualenv
```
boloo_api celery -A boloo_api worker -l info
```

### ⚠️ Production vs Testing 
This mode will allow you to test the sync 
initialisation function with 
```
python manage.py test
```

All the request will be sent to test_routes.
```
DEBUG = True
```
Eith this setting, it will send request to `actual BOL endpoint`
```
DEBUG = False
```


## Routes
After start running the server, check tese routes
- ### a). CRUD for adding seller shop credentials
  [http://127.0.0.1:8000/shop_credentials]

  [http://127.0.0.1:8000/shop_credentials/{shop-ID}]

- ### b). API to list the shipments which are saved
      I decided to create table for each component.
      Following star schema model, allows faster query.
      Shipmen{shipmentId} - other details{shipmentId}, FK is shipmentId.
  [http://127.0.0.1:8000/shipments/]

  [http://127.0.0.1:8000/shipments_item/]

  [http://127.0.0.1:8000/transport/]

  [http://127.0.0.1:8000/customer_details/]

  [http://127.0.0.1:8000/billing_details/]

- ### c). API to start the initial sync of the Shop
  ```py
  url = "http://127.0.0.1:8000/update_shipment"

  payload = '{\r\n    "shop_name":["boloo"]\r\n}'
  headers = {"Content-Type": "application/json"}

  response = requests.request("POST", url, headers=headers, data=payload)
  ```
  as a payload provide name of the shop or shops in the list format.
  ```py
  payload = json.dumps({"shop_name":['boloo', 'shop1', 'shop2']})
  ```


## What should be implemented
- #### 1).  I used djangorestframework
- #### 2).  Created class `RateLimitHandler` in `bol_client/tasks.py` 
        Eachtime API call is made to bol, I save this along with 
        shopID to the shopRequestLog, making sure that in the last 
        1hr a shop didn't make more than 200000 calls. 
- #### 3).
- #### 4). Status code based Exception handling, 
        Auto token refresh at `RequestHandler` in `bol_client/tasks.py`
- #### 5). Used `ThreadPoolExecutor` at `bol_client/views.py`
        When list of shops are posted, below Class will handle 
        the request by passing it to thread workers. 
        Celery will execute the task as work is distributed to 
        each thread. 
```py
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
```

### 🐞 Bugs or Thing I should have done 

= Always get encoded to %3d...
```py
        firfilment_list = [
            f"https://api.bol.com/retailer/shipments?page={counter}?filfilment-method=FBR",
            f"https://api.bol.com/retailer/shipments?page={counter}?filfilment-method=FBB"
        ]
```
Use MySQL, but since I'm not deplying to cloud yet...