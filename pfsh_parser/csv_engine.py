import pycountry
import pandas as pd
from pfsh_parser.log_engine import LogEngine
from pfsh_parser.creds import LOG_FILE
from pfsh_parser.shopify_engine import ShopifyClient


def daily_inventory_parser(csv_file, master_file):
    # Mapping of CSV headers to master file headers
    logger = LogEngine(file_path=LOG_FILE)
    header_mapper = {
        "AV": "Variant Inventory Qty",
        "Item#": "Metafield: custom.item_number [number_integer]",
        "Description": "Title",
        "Manufacturer": "Vendor",
        "Size": "Option1 Value",
        "Category": "Metafield: custom.gender_category [single_line_text_field]",
        "Retail": "Variant Price",
        "Cost": "Variant Cost",
        "COO": "Variant Country of Origin",
        "UPC": "Variant SKU [ID]",
        "MFGUPC": " Variant Barcode",
    }
    logger.log("INVENTORY: LOADING BASE INVENTORY FILE")
    # Load the CSV file and preprocess
    jcbeaninv_df = pd.read_csv(csv_file, encoding="ISO-8859-1")
    # Drop the 'Reference' column if it exists
    logger.log("INVENTORY: DROPPING UNEEDED COLUMNS FROM BASE INVENTORY FILE")
    jcbeaninv_df.drop(columns=["Reference"], errors="ignore", inplace=True)
    # Map the CSV file headers to the master file headers
    logger.log("INVENTORY: MAPPING HEADER COLUMNS TO MATCH")
    jcbeaninv_df.columns = [header_mapper.get(col, col) for col in jcbeaninv_df.columns]

    # Load the master inventory file
    logger.log("INVENTORY: LOADING MASTER INVENTORY FILE")
    final_cleaned_df = pd.read_excel(master_file, engine="openpyxl")

    # Merge the CSV data with the master file based on the item number,
    # updating only if the CSV provides new
    # information
    logger.log("INVENTORY: MERGING COLUMNS")
    for column in jcbeaninv_df.columns:
        if column in final_cleaned_df.columns and column != "Variant SKU [ID]":
            # Create a temporary merged DataFrame to extract updated values
            temp_merged_df = final_cleaned_df.merge(
                jcbeaninv_df[["Variant SKU [ID]", column]],
                on="Variant SKU [ID]",
                how="left",
                suffixes=("", "_updated"),
            )
            # Update the original master DataFrame column with the new values from CSV where applicable
            final_cleaned_df[column] = temp_merged_df[
                column + "_updated"
            ].combine_first(final_cleaned_df[column])

    # Save the updated master file to a new file
    logger.log("INVENTORY: GENERATING NEW FILE")
    updated_final_cleaned_path = "files/tmp/updated_master_inventory.xlsx"
    final_cleaned_df.to_excel(updated_final_cleaned_path, index=False)


def order_parser(shop_name, status, access_token):
    logger = LogEngine(file_path=LOG_FILE)
    logger.log("Fetching Orders from API endpoint")
    sh_client = ShopifyClient(shop_name, access_token)
    orders = sh_client.get_orders(status)
    order_list = []
    column_names = [
        "PONUMBER",
        "ITEM",
        "QTYORDERED",
        "ORDUNIT",
        "SHPNAME(30)",
        "SHPADDR1(30) - DO NOT LEAVE BLANK",
        "SHPADDR2(30)",
        "SHPCITY(16)",
        "SHPSTATE(2)",
        "SHPCOUNTRY(3)",
        "SHPZIP(10)",
    ]

    # Initialize the DataFrame with column names to ensure headers are always present
    logger.log("Setting headers for CSV")
    df = pd.DataFrame(columns=column_names)
    for data in orders:
        for fulfillment in data["fulfillments"]:
            for line_item in fulfillment["line_items"]:
                # get the sheravlen product ID
                product_metafields = sh_client.get_product_metafields(line_item["id"])
                if product_metafields:
                    for item in product_metafields:
                        if item.get("key") == "item_number":
                            sheralven_item_id = item.get("value")
                else:
                    sheralven_item_id = "N/A"
                order_list.append(
                    {
                        "PONUMBER": fulfillment["id"],
                        "ITEM": sheralven_item_id,
                        "QTYORDERED": line_item["quantity"],
                        "ORDUNIT": "EA",
                        "SHPNAME(30)": data["shipping_address"]["name"],
                        "SHPADDR1(30) - DO NOT LEAVE BLANK": data["shipping_address"][
                            "address1"
                        ],
                        "SHPADDR2(30)": data["shipping_address"]["address2"],
                        "SHPCITY(16)": data["shipping_address"]["city"],
                        "SHPSTATE(2)": data["shipping_address"]["province_code"],
                        "SHPCOUNTRY(3)": data["shipping_address"]["country_code"],
                        "SHPZIP(10)": data["shipping_address"]["zip"],
                    }
                )

    if order_list:  # Only update df if there are orders
        logger.log("Orders found - flattening data")
        df = pd.json_normalize(order_list)
    logger.log("Writing CSV File with fetched order data")
    df.to_csv("files/tmp/adjusted_orders_file.csv", index=False)


def shipping_parser(csv_file, shop_name, access_token):
    logger = LogEngine(file_path=LOG_FILE)
    sh_client = ShopifyClient(shop_name, access_token)
    # orders = sh_client.get_orders("fulfilled")
    orders_df = pd.read_csv(f"files/tmp/{csv_file}")
    for index, row in orders_df.iterrows():
        fullfilment_id = sh_client.get_order_fulfillment_id(row["PO NUMBER"])
        if fullfilment_id and row["TRACKINGNUM"]:
            sh_client.update_fulfillment_shipping(fullfilment_id, row["TRACKINGNUM"])
            logger.log(
                f"updated tracking info for {fullfilment_id} with {row['TRACKINGNUM']}"
            )
        else:
            logger.log("no tracking info for order")


def country_to_iso(country_name):
    try:
        return pycountry.countries.lookup(country_name).alpha_2
    except LookupError:
        # Return the original country name if not found
        return country_name
