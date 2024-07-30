import requests
import csv
import os
from datetime import datetime

# Configuration for API endpoints
API_BASE_URL = "https://stats.explorer.q.org/api/v1/lines"
ACTIVE_ACCOUNTS_ENDPOINT = f"{API_BASE_URL}/activeAccounts"
TXNS_GROWTH_ENDPOINT = f"{API_BASE_URL}/txnsGrowth"
GENERAL_STATS_ENDPOINT = "https://explorer.q.org/api/v2/stats"

# Function to fetch data from API
def fetch_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if 'chart' in data:
            return data['chart']
        return data
    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        return []

# Function to load existing data
def load_existing_data(filename):
    try:
        existing_dates = set()
        with open(filename, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                existing_dates.add(row['date'])
        return existing_dates
    except FileNotFoundError:
        return set()

# Function to save data to CSV
def save_data_to_csv(data, filename, existing_dates, ignore_today=True):
    file_exists = os.path.isfile(filename)
    with open(filename, mode='a', newline='') as file:
        fieldnames = ['date', 'value']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        today_date = datetime.now().strftime('%Y-%m-%d')  # Get today's date in 'YYYY-MM-DD' format
        for row in data:
            if row['date'] not in existing_dates and (not ignore_today or row['date'] != today_date):
                writer.writerow(row)
                existing_dates.add(row['date'])


# Function to save general stats data to CSV
def save_general_stats_to_csv(stats, filename):
    file_exists = os.path.isfile(filename)
    with open(filename, mode='a', newline='') as file:
        fieldnames = ['timestamp', 'average_block_time', 'coin_price', 'gas_average', 'gas_fast', 'gas_slow', 
                      'gas_used_today', 'market_cap', 'network_utilization_percentage', 'static_gas_price', 
                      'total_addresses', 'total_blocks', 'total_gas_used', 'total_transactions', 'transactions_today']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        
        # Format the timestamp for the CSV file
        stats['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Ensure gas_prices is properly extracted and removed
        gas_prices = stats.pop('gas_prices', {})
        if gas_prices:
            stats['gas_average'] = gas_prices.get('average', '')
            stats['gas_fast'] = gas_prices.get('fast', '')
            stats['gas_slow'] = gas_prices.get('slow', '')
        else:
            stats['gas_average'], stats['gas_fast'], stats['gas_slow'] = '', '', ''
        
        # Check if all necessary fields are in stats; if not, set them to an empty string
        for field in fieldnames:
            if field not in stats or stats[field] is None:
                stats[field] = ''
                
        writer.writerow(stats)



# Function to upload CSV to Dune
def upload_to_dune(csv_path, space, tablename):
    url = f"https://api.dune.com/api/v1/table/{space}/{tablename}/insert"
    headers = {
        "X-DUNE-API-KEY": "your_api_key_here",  # Replace with your actual Dune API key
        "Content-Type": "text/csv"
    }
    with open(csv_path, "rb") as data:
        response = requests.post(url, data=data, headers=headers)
        print(f"Upload response for {space}/{tablename}: {response.text}")

# Main execution function
def main():
    # Fetch data from APIs
    active_accounts_data = fetch_data(ACTIVE_ACCOUNTS_ENDPOINT)
    transactions_growth_data = fetch_data(TXNS_GROWTH_ENDPOINT)
    general_stats_data = fetch_data(GENERAL_STATS_ENDPOINT)
    
    # Load existing data and update CSVs
    existing_active_accounts = load_existing_data('active_accounts_data.csv')
    existing_transactions_growth = load_existing_data('transactions_growth_data.csv')
    save_data_to_csv(active_accounts_data, 'active_accounts_data.csv', existing_active_accounts)
    save_data_to_csv(transactions_growth_data, 'transactions_growth_data.csv', existing_transactions_growth, ignore_today=True)
    
    # Save general stats data
    save_general_stats_to_csv(general_stats_data, 'general_stats_data.csv')

    # Define your Dune space identifier
    dune_space = 'your_space_identifier'  # Replace with your actual space identifier

    # Upload data to Dune with specified space and table names
    upload_to_dune('active_accounts_data.csv', dune_space, 'active_accounts')
    upload_to_dune('transactions_growth_data.csv', dune_space, 'transactions_growth')
    upload_to_dune('general_stats_data.csv', dune_space, 'general_stats')

if __name__ == "__main__":
    main()
