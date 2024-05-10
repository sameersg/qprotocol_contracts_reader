import requests
import json

# URL to create the table on Dune
url = "https://api.dune.com/api/v1/table/create"

# Payload containing the details of the table to be created
payload = {
    "namespace": "your_username",  # Replace 'your_username' with your actual namespace
    "table_name": "general_stats_data",  # Specify the desired name of your table
    "description": "A table to store various metrics related to cryptocurrencies and blockchain stats.",
    "schema": [
        {"name": "timestamp", "type": "timestamp"},
        {"name": "average_block_time", "type": "double"},
        {"name": "coin_price", "type": "double"},
        {"name": "gas_average", "type": "double"},
        {"name": "gas_fast", "type": "double"},
        {"name": "gas_slow", "type": "double"},
        {"name": "gas_used_today", "type": "double"},
        {"name": "market_cap", "type": "double"},
        {"name": "network_utilization_percentage", "type": "double"},
        {"name": "static_gas_price", "type": "double"},
        {"name": "total_addresses", "type": "double"},
        {"name": "total_blocks", "type": "double"},
        {"name": "total_gas_used", "type": "double"},
        {"name": "total_transactions", "type": "double"},
        {"name": "transactions_today", "type": "double"},
    ],
    "is_private": False  # Set to True if you want the table to be private
}

# Headers including the required API key
headers = {
    "X-DUNE-API-KEY": "your_api_key",  # Replace 'your_api_key' with your actual Dune API key
    "Content-Type": "application/json"
}

# Send POST request to create the table
response = requests.post(url, json=payload, headers=headers)

# Print the response from the server
print(response.status_code)
print(response.text)
