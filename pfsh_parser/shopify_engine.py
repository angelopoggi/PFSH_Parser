import requests
import pandas as pd


def fetch_orders(shop_name, status, access_token):
    url = f"https://{shop_name}/admin/api/2023-01/orders.json?status={status}"
    headers = {
        "X-Shopify-Access-Token": access_token,
        "Content-Type": "application/json",
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()["orders"]
    else:
        return None


def fetch_product(product_id, access_token):
    url = f"/admin/api/2024-01/products/{product_id}.json"
    headers = {
        "X-Shopify-Access-Token": access_token,
        "Content-Type": "application/json",
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return None


def get_product_metafields(shop_url, access_token, product_id):
    url = f"https://{shop_url}/admin/api/2023-01/products/{product_id}/metafields.json"
    headers = {
        "X-Shopify-Access-Token": access_token,
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()[
            "metafields"
        ]  # Returns a list of metafields for the product
    else:
        print(f"Failed to fetch metafields for product {product_id}")
        return None
