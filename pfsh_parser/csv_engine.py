import pycountry
import pandas as pd
from pfsh_parser.log_engine import LogEngine
from pfsh_parser.creds import LOG_FILE


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
        "MFGUPC": "Barcode",
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


def order_parser(csv_file):
    # Original mapping of headers to be replaced
    logger = LogEngine(file_path=LOG_FILE)
    header_mapper = {
        "PONUMBER": "ID",
        "SHPNAME(30)": "Shipping: Name",
        "SHPADDR1(30) - DO NOT LEAVE BLANK": "Shipping: Address 1",
        "SHPADDR2(30)": "Shipping: Address 2",
        "SHPCITY(16)": "Shipping: City",
        "SHPSTATE(2)": "Shipping: Province Code",
        "SHPZIP(10)": "Shipping: Zip",
        "SHPCOUNTRY(3)": "Shipping: Country Code",
        "SHIPVIA": "",
        "ITEM": "Metafield: custom.item_number [number_integer]",
        "QTYORDERED": "Line: Quantity",
        "ORDUNIT": "",
        "PRIUNTPRC": "Line: Price",
    }

    logger.log("ORDERS: LOADING EXPORTED CSV FILE")
    # Read the CSV file into a DataFrame
    df = pd.read_csv(csv_file)

    logger.log("ORDERS: DROPPING SHIPPING LINE COLUMN")
    if "Line: Type" in df.columns:
        df = df[df["Line: Type"] != "Shipping Line"]
        df.drop(columns=["Line: Type"], inplace=True)
    logger.log("ORDERS: MAPPING COLUMNS")
    reverse_mapper = {value: key for key, value in header_mapper.items() if value}
    new_columns = {col: reverse_mapper.get(col, col) for col in df.columns}
    df.rename(columns=new_columns, inplace=True)
    df["ORDUNIT"] = "EA"

    logger.log("ORDERS: GENERATING NEW ORDERS FILE")
    output_path = "files/tmp/adjusted_orders_file.csv"
    df.to_csv(output_path, index=False)


def calculate_sale_price(retail_price, percent_off):
    discount_price = (int(retail_price) * int(percent_off)) // 100
    return retail_price - discount_price


def country_to_iso(country_name):
    try:
        return pycountry.countries.lookup(country_name).alpha_2
    except LookupError:
        # Return the original country name if not found
        return country_name
