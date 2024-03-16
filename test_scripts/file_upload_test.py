import requests
import unittest
#from your_parser_module import clean_price, parse_csv_file


url = "http://localhost:8000/api/orders/upload/"
files = {'file': open('/Users/damilare/Documents/text_files/todays_combine.csv', 'rb')}

csv_data = """Procurement Officer,Product,Quantity,Price
OFFICE,Blueband Butter (450g),1.0 piece,2419.0
OFFICE,Dangote Sugar (1kg),4.0 pack,9596.0
OFFICE,Emma Coconut Powder (1 Piece),3.0 piece,2637.0"""


#response = requests.post(url, files=files)
response = requests.post(url, data=csv_data)

print(response.text)



# class TestCSVParser(unittest.TestCase):
#     def test_clean_price(self):
#         # Test cleaning of price values with special characters
#         price_with_special_chars = '√¢‚Äö¬¶2419.0'
#         cleaned_price = clean_price(price_with_special_chars)
#         self.assertEqual(cleaned_price, 2419.0)

#         # Add more test cases for different scenarios as needed

#     def test_parse_csv_file(self):
#         # Test parsing of a sample CSV file
#         csv_file_path = '/Users/damilare/Documents/text_files/todays_combine.csv'
#         orders = parse_csv_file(csv_file_path)

#         # Verify that orders are correctly parsed
#         self.assertEqual(len(orders), 7)  # Adjust expected number of orders
#         # Add more assertions to verify the content of parsed orders

# if __name__ == '__main__':
#     unittest.main()
