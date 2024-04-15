import requests
import json
from typing import Optional
import pprint


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
        response = self._get(f"/admin/api/2024-04/orders.json?status={status}")
        if response.ok:
            return response.json()["orders"]
        else:
            return response.raise_for_status()

    def get_product(self, product_id):
        response = self._get(f"/admin/api/2024-04/products/{product_id}.json")
        if response.status_code.ok:
            return response.json()
        else:
            return response.raise_for_status()

    def get_product_metafields(self, product_id):
        response = self._get(
            f"/admin/api/2024-04/products/{product_id}/metafields.json"
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
            f"/admin/api/2024-04/fulfillments/{fulfillment_id}/update_tracking.json",
            data=json.dumps(shipping_payload),
        )
        if response.status_code == 200:
            return response.json()
        else:
            return response.raise_for_status()

    def _check_fulfillment_status(self, fulfillment_order_id):
        response = self._get(
            f"/admin/api/2024-04/fulfillment_orders/{fulfillment_order_id}.json"
        )
        if response.ok:
            if response.json()["fulfillment_order"]["status"] == "closed":
                return False
            else:
                return True
        else:
            response.raise_for_status()

    def create_fulfillment(self, fulfillment_order_id_list) -> dict:
        """
        Create a fulfillment for an order.

        Args:
            order_id (str): The ID of the order to fulfill.
            location_id (int): The ID of the location from which the items will be fulfilled.
            line_items (list): A list of line item dictionaries to be fulfilled.
            notify_customer (bool, optional): Whether to notify the customer via email. Defaults to False.

        Returns:
            dict: The JSON response from the Shopify API.
        """
        # check to make sure the fulfillment is open and not closed
        for fulfillment_order_id in fulfillment_order_id_list:
            fulfillment_status = self._check_fulfillment_status(fulfillment_order_id)
            if fulfillment_status:
                fulfillment_payload = {
                    "fulfillment": {
                        "message": "Thank you for your order! Your order was received and we are currently processing it.",
                        "notify_customer": True,
                        "line_items_by_fulfillment_order": [
                            {"fulfillment_order_id": fulfillment_order_id}
                        ],
                    }
                }
                response = self._post(
                    f"/admin/api/2024-04/fulfillments.json",
                    json_data=fulfillment_payload,
                )
                if response.status_code == 200:
                    return response.json()
                else:
                    return response.raise_for_status()
            else:
                print(
                    f"Fulfillment Order {fulfillment_order_id} marked as closed - nothing to do"
                )

    # def get_order_fulfillment_id(self, order_id):
    #     response = self._get(f"/admin/api/2024-04/orders/{order_id}.json")
    #     pprint.pprint(response.json())
    #     if response.ok:
    #         for item in response.json()['fulfillment_orders']:
    #             if item['status'] != "closed":
    #                 return item['id']
    #     else:
    #         return response.raise_for_status()

    def get_fulfillment_order_id(self, order_id):
        response = self._get(
            f"/admin/api/2024-04/orders/{order_id}/fulfillment_orders.json"
        )
        fulfillment_orders = []
        if response.ok:
            for item in response.json()["fulfillment_orders"]:
                fulfillment_orders.append(item["id"])
            return fulfillment_orders
        else:
            return response.raise_for_status()

    def get_variant_cost(self, item_id, item_sku):
        # we need to get the iventory ID from the product ID
        product_reponse = self._get(f"/admin/api/2024-04/products/{item_id}.json")
        if not product_reponse.ok:
            return product_reponse.raise_for_status()
        for item in product_reponse.json()["product"]["variants"]:
            if item["sku"] == item_sku:
                inventory_id = item["inventory_item_id"]
                break
        inventory_response = self._get(
            f"/admin/api/2024-04/inventory_items/{inventory_id}.json"
        )
        if inventory_response.ok:
            return inventory_response.json()["inventory_item"]["cost"]
        else:
            return inventory_response.raise_for_status()
