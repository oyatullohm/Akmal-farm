from requests.auth import HTTPBasicAuth
from .models import Product , Category
from celery import shared_task
import requests
import datetime
import logging
import redis
import json

logger = logging.getLogger('celery_tasks')
r = redis.Redis(host='localhost', port=6379, db=0)

@shared_task
def refresh_products_cache():
    url = "http://93.170.11.10:8088/RM_OPT/hs/online/stock"
    username = "Online"
    password = "cJXGLytPHb3nDNZf5gRh7jzwa"
    response = requests.post(url, auth=HTTPBasicAuth(username, password), stream=True, json={})
    if response.status_code == 200:
        data = response.json().get('array', [])
        uid_list = [item["UID"] for item in data]
        products = Product.objects.filter(uid__in=uid_list)
        products_dict = {p.uid: p for p in products}
        
        result = []
        for item in data:
            # category =  Category.objects.get_or_create(name=item['Class'])
            product = products_dict.get(int(item["UID"]))
            logger.info(f"{item}")

            if product:
                result.append({
                    "id": product.id,
                    "name": item.get("Name", ""),  # agar "Name" yoq bolsa "" qaytaradi
                    "price": item.get("Price", 0),
                    "class": item.get("Class", ""),
                    "producer": item.get("Producer", ""),
                    "country": item.get("Country", ""),
                    "MNN": item.get("MNN", ""),
                    "ReleaseForm": item.get("ReleaseForm", ""),
                    "ProductType": item.get("ProductType", ""),
                    "ExpDate": item.get("ExpDate", ""),  # E'tibor bering: yozishingizda xatolik bor: "ProdExpDateuctType"
                    "image1": product.image1.url if product.image1 else ""
                })

        r.setex('final_result', 3600*24, json.dumps(result))
        print("Redis cache updated successfully!")
        # print(result)
        logger.info(f"Redis cache updated successfully! {datetime.datetime.now()}")
    else:
        logger.error(f"Failed to refresh product data! Status code: {response.status_code}")
