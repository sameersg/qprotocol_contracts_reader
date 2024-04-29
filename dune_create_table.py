import requests
import json

# URL to create the table on Dune
url = "https://api.dune.com/api/v1/table/create"

# Payload containing the details of the table to be created
payload = {
    "namespace": "{USERNAME}",  # Replace with your namespace
    "table_name": "{TABLENAME}",
    "description": "A table to store various metrics related to cryptocurrencies.",
    "schema": [
        {"name": "date", "type": "timestamp"},
        {"name": "btc_in_usd", "type": "double"},
        {"name": "elk_in_usd", "type": "double"},
        {"name": "vnxau_in_usd", "type": "double"},
        {"name": "weth_in_usd", "type": "double"},
        {"name": "bridged_wbtc", "type": "double"},
        {"name": "bridged_usdc", "type": "double"},
        {"name": "bridged_dai", "type": "double"},
        {"name": "bridged_weth", "type": "double"},
        {"name": "bridged_elk", "type": "double"},
        {"name": "bridged_usd_value", "type": "double"},
        {"name": "total_qusd", "type": "double"},
        {"name": "locked_wbtc", "type": "double"},
        {"name": "locked_usdc", "type": "double"},
        {"name": "locked_dai", "type": "double"},
        {"name": "borrowing_tvl", "type": "double"},
        {"name": "saving_tvl", "type": "double"},
        {"name": "elk_locked_wbtc", "type": "double"},
        {"name": "elk_locked_usdc", "type": "double"},
        {"name": "elk_locked_dai", "type": "double"},
        {"name": "elk_locked_elk", "type": "double"},
        {"name": "elk_locked_qusd", "type": "double"},
        {"name": "elk_locked_vnxau", "type": "double"},
        {"name": "elk_tvl", "type": "double"},
        {"name": "stq_supply", "type": "double"},
        {"name": "total_tvl", "type": "double"}
    ],
    "is_private": False
}

# Headers including the required API key
headers = {
    "X-DUNE-API-KEY": "",
    "Content-Type": "application/json"
}

# Send POST request to create the table
response = requests.post(url, json=payload, headers=headers)

# Print the response from the server
print(response.status_code)
print(response.text)
