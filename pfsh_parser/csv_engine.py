import csv
import pycountry
def daily_inventory_parser(csv_file):
    header_mapper = {
        "AV": "Variant Inventory Qty",
        "Item#": "Variant ID",
        "Description": "Title",
        "Reference": None,
        "Manufacturer": "Vendor",
        "Size": "Option1 Value",
        "Category": "Metafield: custom.gender_category.string",
        "Retail": "Variant Price",
        "% Off": "Variant Compare At Price",
        "Cost": "Variant Cost",
        "COO": "Variant Country of Origin",
        "UPC": "Variant SKU [ID]",
        "MFGUPC": "Barcode"
    }

    #update percent off to actual number
    with open(csv_file, 'r', newline='', encoding="ISO-8859-1") as csv_in, open(f"{csv_file}_MATRIXIFY.csv", "w",
                                                                                newline='') as csv_out:
        reader = csv.DictReader(csv_in)

        # Filter out the None values and prepare the headers for DictWriter
        filtered_headers = {k: v for k, v in header_mapper.items() if v is not None}
        writer = csv.DictWriter(csv_out, fieldnames=filtered_headers.values())
        writer.writeheader()

        for row in reader:
            # Save the values needed
            current_price = float(row["Retail"])
            discount_percent = float(row["% Off"].replace("%", ""))
            new_price = calculate_sale_price(current_price, discount_percent)

            # Prepare the new row based on new headers
            new_row = {new_header: (current_price if old_header == "Retail" else country_to_iso(row[old_header]) if old_header == "COO" else row[old_header]) for old_header, new_header in filtered_headers.items() if old_header in row}
            # Correctly map the "% Off" column to compare at price
            new_row["Variant Compare At Price"] = int(current_price)
            # Write the updated row
            writer.writerow(new_row)


def calculate_sale_price(retail_price, percent_off):
    discount_price = (int(retail_price) * int(percent_off)) // 100
    return retail_price - discount_price

def country_to_iso(country_name):
    try:
        return pycountry.countries.lookup(country_name).alpha_2
    except LookupError:
        # Return the original country name if not found
        return country_name


