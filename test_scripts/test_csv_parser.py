import csv
import re
import pandas as pd


# def parse_excel_file(file_path):
#     orders = []
#     # Read the Excel file into a DataFrame
#     df = pd.read_excel(file_path)
    
#     # Iterate over rows in the DataFrame
#     for index, row in df.iterrows():
#         procurement_officer = row['Procurement Officer']
#         product = row['Product']
#         quantity = float(row['Quantity'].split()[0])  # Extract numeric quantity
#         price = clean_price(row['Price'])  # Clean up price value
        
#         # Create and append order object to orders list
#         orders.append({
#             'procurement_officer': procurement_officer,
#             'product': product,
#             'quantity': quantity,
#             'price': price
#         })
#     return orders

# # Example usage:
# excel_file_path = '/Users/damilare/Documents/text_files/todays_combine.csv'
# orders = parse_excel_file(excel_file_path)
# print(orders)  # Print parsed orders


def clean_price(price_str):
    # Remove non-numeric characters and symbols from the price string
    cleaned_price = re.sub(r'[^\d.]', '', price_str)
    #print(f'cleaned price: {cleaned_price}')
    # Convert the cleaned price to a float
    return float(cleaned_price)



def parse_csv_file(file_path):
    orders = []
    with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)  # No need to specify delimiter for CSV files
        next(reader)  # Skip header row if present
        for row in reader:
            if len(row) < 4:
                print(f"Ignoring row: {row} - Insufficient fields")
                continue  # Skip this row and move to the next one

            procurement_officer = row[0]
            product = row[1]
            quantity = float(row[2].split()[0])  # Extract numeric quantity
            price = clean_price(row[3])  # Clean up price value
            # Create and append order object to orders list
            orders.append({
                'procurement_officer': procurement_officer,
                'product': product,
                'quantity': quantity,
                'price': price
            })
    return orders


# Example usage:
csv_file_path = '/Users/damilare/Documents/text_files/todays_combine.csv'
orders = parse_csv_file(csv_file_path)
print(orders[:10])  # Print parsed orders
