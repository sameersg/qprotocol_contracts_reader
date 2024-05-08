import requests
import csv
import json
import os

def fetch_data(token_address):
    # Fetch token transfer data from a blockchain explorer API
    url = f"https://explorer.q.org/api/v2/tokens/{token_address}/transfers"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching data for token {token_address}: {e}")
        return None

def read_last_processed_timestamp():
    # Read the last processed timestamp from JSON storage
    try:
        with open('last_processed.json', 'r') as file:
            data = json.load(file)
            return data['last_timestamp']
    except FileNotFoundError:
        return None

def update_last_processed_timestamp(timestamp):
    # Update the last processed timestamp in JSON storage
    with open('last_processed.json', 'w') as file:
        json.dump({'last_timestamp': timestamp}, file)

def load_existing_tx_hashes(filename='mint_burn_data.csv'):
    # Load existing transaction hashes from CSV to avoid reprocessing
    try:
        with open(filename, mode='r', newline='') as file:
            reader = csv.DictReader(file)
            return {row['tx_hash'] for row in reader}
    except FileNotFoundError:
        return set()

def process_mint_burn_events(token_address, last_timestamp, seen_tx_hashes):
    # Process minting and burning events and record new data
    data = fetch_data(token_address)
    mint_burn_data = []
    latest_timestamp = last_timestamp

    if data:
        for item in data.get('items', []):
            tx_hash = item['tx_hash']
            timestamp = item['timestamp']
            if item['type'] in ['token_minting', 'token_burning'] and tx_hash not in seen_tx_hashes:
                seen_tx_hashes.add(tx_hash)
                mint_burn_data.append({
                    'tx_hash': tx_hash,
                    'from': item['from']['hash'],
                    'to': item['to']['hash'],
                    'token_name': item['token']['name'],
                    'token_symbol': item['token']['symbol'],
                    'transfer_type': item['type'],
                    'timestamp': timestamp,
                    'value': int(item['total']['value']) / (10 ** int(item['total']['decimals']))
                })
                if not latest_timestamp or timestamp > latest_timestamp:
                    latest_timestamp = timestamp

    if latest_timestamp:
        update_last_processed_timestamp(latest_timestamp)

    return mint_burn_data

def save_data_to_csv(data, filename='mint_burn_data.csv'):
    # Save new minting and burning data to CSV
    file_exists = os.path.isfile(filename)
    with open(filename, mode='a', newline='') as file:
        fieldnames = ['tx_hash', 'from', 'to', 'token_name', 'token_symbol', 'transfer_type', 'timestamp', 'value']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        for row in data:
            writer.writerow(row)

def upload_to_dune(csv_path):
    # Upload data to Dune for analysis
    url = "https://api.dune.com/api/v1/table/{space}/{tablename}/insert"
    headers = {
        "X-DUNE-API-KEY": "",
        "Content-Type": "text/csv"
    }
    with open(csv_path, "rb") as data:
        response = requests.request("POST", url, data=data, headers=headers)
        print(response.text)

if __name__ == "__main__":
    # Main execution block
    existing_tx_hashes = load_existing_tx_hashes()
    last_timestamp = read_last_processed_timestamp()
    tokens = {
        'WETH': '0xd56F9ffF3fe3BD0C7B52afF9A42eb70E05A287Cc',
        'WBTC': '0xde397e6C442A3E697367DecBF0d50733dc916b79',
        'USDC': '0x79Cb92a2806BF4f82B614A84b6805963b8b1D8BB',
        'USDT': '0xCdb1CEaE11E4Dd46E908F01CF85Ed6AB4aE59dcc',
        '0xMR': '0x79187B0D66249ac375EBd94861B344a0Dc170C14',
        'DAI': '0xDeb87c37Dcf7F5197026f574cd40B3Fc8Aa126D1'
    }
    all_events = []
    for token_name, address in tokens.items():
        events = process_mint_burn_events(address, last_timestamp, existing_tx_hashes)
        all_events.extend(events)
        print(f"Processed {token_name} events")

    if all_events:
        csv_file_path = 'mint_burn_data.csv'
        save_data_to_csv(all_events, csv_file_path)
        upload_to_dune(csv_file_path)
    else:
        print("No new events to process.")
