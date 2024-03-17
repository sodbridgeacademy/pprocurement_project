import requests

url = "https://spiritual-anglerfish-sodbridge.koyeb.app/api/login/"

# Define the credentials to be used for login
credentials = {
    'username': 'TAIWO',
    'password': 'taiwo00'
}

# Make a POST request to the login endpoint with the provided credentials
response = requests.post(url, data=credentials)

# Print the response from the server
print(response.text)
