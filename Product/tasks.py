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
        uid_list = []

        for item in data:
            try:
                uid = int(item.get("UID"))
                uid_list.append(uid)
            except (TypeError, ValueError):
                continue

        products = Product.objects.filter(uid__in=uid_list)
        products_dict = {p.uid: p for p in products}

        result = []
        for item in data:
            Category.objects.get_or_create(name=item.get('Class',"class"))
            # try:
            uid = int(item.get("UID"))
            # except (TypeError, ValueError):
            #     continue

            product = products_dict.get(uid)
            if product:      
                result.append({
                    "id": product.id,
                    "name": item.get("Name", ""),
                    'name_lover':item.get("Name").lower(),
                    "price": item.get("Price", 0),
                    "class": item.get("Class", ""),
                    "producer": item.get("Producer", ""),
                    "country": item.get("Country", ""),
                    "MNN": item.get("MNN", ""),
                    "ReleaseForm": item.get("ReleaseForm", ""),
                    "ProductType": item.get("ProductType", ""),
                    "ExpDate": item.get("ExpDate", ""),
                    "info": product.info,
                     "image1": product.image1.url if product.image1 else "",
                    "image2": product.image2.url if product.image2 else "",
                    "image3": product.image3.url if product.image3 else "",
                })

        r.setex('final_result', 3600*24, json.dumps(result))
        # print("Redis cache updated successfully!")
            # print(result)
        logger.info(f"Redis cache updated successfully! {datetime.datetime.now()}")
    # else:
    #     logger.error(f"Failed to refresh product data! Status code: {response.status_code}")
        if response.status_code == 200:
            data = response.json().get('array', [])
        uid_list = []


        for item in data:
            try:
                uid = int(item.get("UID"))
                uid_list.append(uid)
            except (TypeError, ValueError):
                continue


        products = Product.objects.filter(uid__in=uid_list)
        products_dict = {p.uid: p for p in products}
        grouped_by_class = {}


        for item in data:
            try:
                uid = int(item.get("UID"))
            except (TypeError, ValueError):
                continue

            product = products_dict.get(uid)
            if not product:
                continue  # Product topilmagan bo‘lsa, bu itemni o‘tkazib yuboramiz

            category = item.get("Class", "None-Class")
            product_data = {
                "id": product.id,
                "name": item.get("Name", ""),
                "name_lower": item.get("Name", "").lower(),
                "price": item.get("Price", 0),
                "class": category,
                "producer": item.get("Producer", ""),
                "country": item.get("Country", ""),
                "MNN": item.get("MNN", ""),
                "ReleaseForm": item.get("ReleaseForm", ""),
                "ProductType": item.get("ProductType", ""),
                "ExpDate": item.get("ExpDate", ""),
                "info": product.info,
                "image1": product.image1.url if product.image1 else "",
                "image2": product.image2.url if product.image2 else "",
                "image3": product.image3.url if product.image3 else "",
            }

            grouped_by_class.setdefault(category, []).append(product_data)

        logger.info(f"class update! {datetime.datetime.now()}")
        r.setex('products_by_class', 86400, json.dumps(grouped_by_class))
