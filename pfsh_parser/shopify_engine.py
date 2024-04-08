import requests
import json
from typing import Optional


class ShopifyClient:
    def __init__(self, shop_name: str, access_token: str):
        """
        Initialize the ShopifyClient.

        Args:
            shop_name (str): The shop name you wish to make api calls to
            access-token (str): The shopify access token to authenticate
        """
        self.shop_name = shop_name
        self.access_token = access_token
        self.base_url = self._create_url()
        self.session = requests.Session()
        self._set_header()

    def _set_header(self):
        self.session.headers = {
            "X-Shopify-Access-Token": self.access_token,
            "Content-Type": "application/json",
        }

    def _create_url(
        self,
    ) -> str:
        """
        Create the base URL based on the host, port, and HTTPS settings.

        Returns:
            str: The base URL.
        """
        return f"https://{self.shop_name}"

    def _post(self, uri: str, json_data: Optional[dict] = None):
        """
        Perform a POST request to the specified URI.

        Args:
            uri (str): The URI to send the POST request to.
            json_data (Optional[dict]): The JSON data to send with the request. Defaults to None.

        Returns:
            requests.Response: The response object.

        Raises:
            requests.HTTPError: If the request is not successful.
        """
        if json_data:
            response = self.session.post(f"{self.base_url}{uri}", json=json_data)
        else:
            response = self.session.post(f"{self.base_url}{uri}")
        if response.ok:
            return response
        return response.raise_for_status()

    def _put(self, uri: str, json_data: Optional[dict] = None):
        """
        Perform a PUT request to the specified URI.

        Args:
            uri (str): The URI to send the POST request to.
            json_data (Optional[dict]): The JSON data to send with the request. Defaults to None.

        Returns:
            requests.Response: The response object.

        Raises:
            requests.HTTPError: If the request is not successful.
        """
        if json_data:
            response = self.session.put(f"{self.base_url}{uri}", json=json_data)
        else:
            response = self.session.put(f"{self.base_url}{uri}")
        if response.ok:
            return response
        return response.raise_for_status()

    def _get(self, uri: str):
        """
        Perform a GET request to the specified URI.

        Args:
            uri (str): The URI to send the GET request to.

        Returns:
            requests.Response: The response object.

        Raises:
            requests.HTTPError: If the request is not successful.
        """
        response = self.session.get(f"{self.base_url}{uri}")
        if response.ok:
            return response
        return response.raise_for_status()

    def get_orders(self, status):
        response = self._get(f"/admin/api/2023-01/orders.json?status={status}")
        if response.ok:
            return response.json()["orders"]
        else:
            return response.raise_for_status()

    def get_product(self, product_id):
        response = self._get(f"/admin/api/2024-01/products/{product_id}.json")
        if response.status_code.ok:
            return response.json()
        else:
            return response.raise_for_status()

    def get_product_metafields(self, product_id):
        response = self._get(
            f"/admin/api/2023-01/products/{product_id}/metafields.json"
        )
        if response.status_code == 200:
            return response.json()[
                "metafields"
            ]  # Returns a list of metafields for the product
        else:
            print(f"Failed to fetch metafields for product {product_id}")
            return None

    def update_fulfillment_shipping(self, fulfillment_id, tracking_number):
        shipping_payload = {
            {"notify_customer": "true", "tracking_info": {"number": tracking_number}}
        }
        response = self._post(
            f"/admin/api/2024-01/fulfillments/{fulfillment_id}/update_tracking.json",
            data=json.dumps(shipping_payload),
        )
        if response.status_code == 200:
            return response.json()
        else:
            return response.raise_for_status()

    def get_order_fulfillment_id(self, order_id):
        response = self._get(f"/admin/api/2023-01/orders/{order_id}.json")
        if response.status_code == 200:
            return response.json()["order"]["fulfillments"]
        else:
            return response.raise_for_status()
