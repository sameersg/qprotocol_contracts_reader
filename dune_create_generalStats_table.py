import requests
import json
from dotenv import load_dotenv
import os

# Load environment variables from the .env file
load_dotenv()

# Get API key, namespaces, and table names from environment variables
api_key = os.getenv("DUNE_API_KEY")
namespace_one = os.getenv("NAMESPACE1")
table_name_one = os.getenv("TABLE_NAME1")

# URL to create the table on Dune
url = "https://api.dune.com/api/v1/table/create"

# Choose namespace and table dynamically (example for first API)
namespace = namespace_one  # or namespace_two for the other API
table_name = table_name_one  # or table_name_two for the other API

# Payload containing the details of the table to be created
payload = {
    "namespace": namespace,
    "table_name": table_name,
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
    "is_private": False
}

# Headers including the API key
headers = {
    "X-DUNE-API-KEY": api_key,
    "Content-Type": "application/json"
}

# Send POST request to create the table
response = requests.post(url, json=payload, headers=headers)

# Print the response from the server
print(response.status_code)
print(response.text)