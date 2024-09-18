import requests
import json
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get values from .env
DUNE_API_KEY = os.getenv("DUNE_API_KEY")
NAMESPACE = os.getenv("NAMESPACE1")
TABLE_NAME = os.getenv("TABLE_NAME1")

# URL to create the table on Dune
url = "https://api.dune.com/api/v1/table/create"

# Payload containing the details of the table to be created
payload = {
    "namespace": NAMESPACE,  # Use environment variable for namespace
    "table_name": TABLE_NAME,  # Use environment variable for table_name
    "description": "A table to store various metrics related to cryptocurrencies.",
    "schema": [
        {"name": "date", "type": "timestamp"},
        {"name": "btc_in_usd", "type": "double"},
        {"name": "elk_in_usd", "type": "double"},
        {"name": "vnxau_in_usd", "type": "double"},
        {"name": "weth_in_usd", "type": "double"},
        {"name": "stq_conv_rate", "type": "double"},
        {"name": "bridged_wbtc", "type": "double"},
        {"name": "bridged_usdc", "type": "double"},
        {"name": "bridged_dai", "type": "double"},
        {"name": "bridged_weth", "type": "double"},
        {"name": "bridged_elk", "type": "double"},
        {"name": "total_qusd", "type": "double"},
        {"name": "locked_wbtc", "type": "double"},
        {"name": "locked_usdc", "type": "double"},
        {"name": "locked_dai", "type": "double"},
        {"name": "saving_tvl", "type": "double"},
        {"name": "elk_locked_wbtc", "type": "double"},
        {"name": "elk_locked_usdc", "type": "double"},
        {"name": "elk_locked_dai", "type": "double"},
        {"name": "elk_locked_elk", "type": "double"},
        {"name": "elk_locked_qusd", "type": "double"},
        {"name": "elk_locked_vnxau", "type": "double"},
        {"name": "stq_supply", "type": "double"},
        {"name": "extra_1", "type": "double"},
        {"name": "extra_2", "type": "double"},
        {"name": "extra_3", "type": "double"},
        {"name": "extra_4", "type": "double"},
        {"name": "extra_5", "type": "double"},
        {"name": "extra_6", "type": "double"},
        {"name": "extra_7", "type": "double"},
        {"name": "extra_8", "type": "double"},
        {"name": "extra_9", "type": "double"},
        {"name": "extra_10", "type": "double"},
        {"name": "extra_11", "type": "double"},
        {"name": "extra_12", "type": "double"},
        {"name": "extra_13", "type": "double"},
        {"name": "extra_14", "type": "double"},
        {"name": "extra_15", "type": "double"},
        {"name": "extra_16", "type": "double"},
        {"name": "extra_17", "type": "double"},
        {"name": "extra_18", "type": "double"},
        {"name": "extra_19", "type": "double"},
        {"name": "extra_20", "type": "double"},
    ],
    "is_private": False
}

# Headers including the required API key
headers = {
    "X-DUNE-API-KEY": DUNE_API_KEY,  # Use environment variable for API key
    "Content-Type": "application/json"
}

# Send POST request to create the table
response = requests.post(url, json=payload, headers=headers)

# Print the response from the server
print(response.status_code)
print(response.text)