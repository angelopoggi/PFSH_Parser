import requests
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
        """
        Retrieve orders based on their status.

        Args:
        status (str): The status of the orders to retrieve.

        Returns:
        list: A list of orders if any are found, None otherwise.
        Raises:
        Exception: If the HTTP request failed or if an unexpected error occurs.
        """
        try:
            response = self._get(f"/admin/api/2024-04/orders.json?status={status}")
            response.raise_for_status()  # This will raise an HTTPError if the HTTP request returned an unsuccessful status code.

            if "application/json" in response.headers.get("Content-Type", ""):
                data = response.json()
                if data and "orders" in data:
                    return data["orders"]
                return None
            else:
                # Handle cases where the response doesn't contain JSON data
                print(
                    "Invalid content type received: %s",
                    response.headers.get("Content-Type"),
                )
                return None
        except requests.HTTPError as http_err:
            print(
                f"HTTP error occurred: {http_err}"
            )  # Log the error or handle it otherwise
            raise
        except Exception as err:
            print(f"An error occurred: {err}")
            raise

    def get_unshipped_orders(self):
        orders = self.get_orders("open")
        order_list = []
        for order in orders:
            order_list.append(order["id"])
        return order_list

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
            "fulfillment": {
                "notify_customer": "true",
                "tracking_info": {"number": str(tracking_number)},
            }
        }
        response = self._post(
            f"/admin/api/2024-04/fulfillments/{fulfillment_id}/update_tracking.json",
            json_data=shipping_payload,
        )
        if response.status_code == 200:
            print(
                f"Tracking number {str(tracking_number)} updated for fulfillemnt {fulfillment_id}"
            )
            return response.json()
        else:
            return response.raise_for_status()

    def close_order(self, order_id):
        response = self._post(f"/admin/api/2024-04/orders/{order_id}/close.json")
        if response.ok:
            print(f"Order {order_id} was marked as closed")
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
                    f"Fulfillment Order {fulfillment_order_id} marked as closed - no need to create fulfillment"
                )

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

    def get_fulfillments_by_fulfillment_order_id(self, fulfillment_order_id_list):
        fulfillment_list = []
        for item in fulfillment_order_id_list:
            if self._check_fulfillment_status(item):
                response = self._get(
                    f"/admin/api/2024-04/fulfillment_orders/{item}/fulfillments.json"
                )
                if response.ok:
                    for fulfillment in response.json()["fulfillments"]:
                        fulfillment_list.append(fulfillment["id"])
                    return fulfillment_list
                else:
                    return response.raise_for_status()
            else:
                print(
                    f"fulfillment order id {item} is marked as closed - nothing to pull"
                )

    def get_fulfillments_by_order_id(self, order_id):
        fulfillment_list = []
        response = self._get(f"/admin/api/2024-04/orders/{order_id}/fulfillments.json")
        if response.ok:
            for fulfillment in response.json()["fulfillments"]:
                if fulfillment["status"] == "success":
                    fulfillment_list.append(fulfillment["id"])
            return fulfillment_list
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

    def get_order_risk(self, order_id):
        response = self._get(f"/admin/api/2024-04/orders/{order_id}/risks.json")
        if response.ok:
            return response.json()
        else:
            return response.raise_for_status()

    def get_order_risk_number(self, order_id):
        response = self._get(f"/admin/api/2024-04/orders/{order_id}/risks.json")
        if response.ok:
            return (response.json()["risks"]['score'])
        else:
            return response.raise_for_status()