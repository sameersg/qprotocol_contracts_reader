import requests
import csv
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get values from .env
DUNE_API_KEY = os.getenv("DUNE_API_KEY")
NAMESPACE1 = os.getenv("NAMESPACE1")
TABLE_NAME1 = os.getenv("TABLE_NAME1")
TABLE_NAME3 = os.getenv("TABLE_NAME3")
TABLE_NAME4 = os.getenv("TABLE_NAME4")

# Configuration for API endpoints
API_BASE_URL = "https://stats.explorer.q.org/api/v1/lines"
ACTIVE_ACCOUNTS_ENDPOINT = f"{API_BASE_URL}/activeAccounts"
TXNS_GROWTH_ENDPOINT = f"{API_BASE_URL}/txnsGrowth"
GENERAL_STATS_ENDPOINT = "https://explorer.q.org/api/v2/stats"

# Define the user and table names for Dune upload
dune_user = NAMESPACE1  # Use namespace from .env
dune_table_active_accounts = TABLE_NAME4  # Use table name for active accounts from .env
dune_table_transactions_growth = TABLE_NAME3  # Use table name for transactions growth from .env
dune_table_general_stats = TABLE_NAME1  # Use table name for general stats from .env
api_key = DUNE_API_KEY  # Use API key from .env

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
        print(f"Error fetching data from {url}: {e}")
        return []

# Function to load existing data
def load_existing_data(filename, date_key='date'):
    try:
        existing_dates = set()
        with open(filename, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                existing_dates.add(row[date_key])
        print(f"Loaded existing data from {filename}.")
        return existing_dates
    except FileNotFoundError:
        print(f"No existing data found for {filename}. Starting fresh.")
        return set()

# Function to save data to CSV
def save_data_to_csv(data, filename, existing_dates, ignore_today=True):
    file_exists = os.path.isfile(filename)
    with open(filename, mode='a', newline='') as file:
        fieldnames = ['date', 'value']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
            print(f"Created new CSV file {filename}.")
        today_date = datetime.now().strftime('%Y-%m-%d')  # Get today's date in 'YYYY-MM-DD' format
        for row in data:
            if row['date'] not in existing_dates and (not ignore_today or row['date'] != today_date):
                writer.writerow(row)
                existing_dates.add(row['date'])
        print(f"Saved data to {filename}.")

# Function to save general stats data to CSV
def save_general_stats_to_csv(stats, filename, existing_timestamps):
    file_exists = os.path.isfile(filename)
    with open(filename, mode='a', newline='') as file:
        fieldnames = ['timestamp', 'average_block_time', 'coin_price', 'gas_average', 'gas_fast', 'gas_slow', 
                      'gas_used_today', 'market_cap', 'network_utilization_percentage', 'static_gas_price', 
                      'total_addresses', 'total_blocks', 'total_gas_used', 'total_transactions', 'transactions_today']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
            print(f"Created new general stats CSV file {filename}.")
        
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
        print(f"Saved general stats to {filename}.")

# Function to upload CSV to Dune
def upload_to_dune(csv_path, space, tablename):
    url = f"https://api.dune.com/api/v1/table/{space}/{tablename}/insert"
    headers = {
        "X-DUNE-API-KEY": api_key,  # Use the Dune API key variable
        "Content-Type": "text/csv"
    }
    with open(csv_path, "rb") as data:
        response = requests.post(url, data=data, headers=headers)
        print(f"Upload response for {space}/{tablename}: {response.text}")

# Function to create a temporary CSV file with new data
def create_temp_csv(new_data, filename, fieldnames):
    if not new_data:
        print(f"No new data to write to {filename}. Skipping temporary file creation.")
        return None

    temp_filename = f"temp_{filename}"
    with open(temp_filename, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(new_data)
    print(f"Created temporary CSV file {temp_filename} for upload.")
    return temp_filename

# Main execution function
def main():
    # Manually set this flag to True for the first run, then False for subsequent runs
    first_run = False

    # Fetch data from APIs
    print("Fetching data from APIs...")
    active_accounts_data = fetch_data(ACTIVE_ACCOUNTS_ENDPOINT)
    transactions_growth_data = fetch_data(TXNS_GROWTH_ENDPOINT)
    general_stats_data = fetch_data(GENERAL_STATS_ENDPOINT)

    # Load existing data and update CSVs
    existing_active_accounts = load_existing_data('active_accounts_data.csv')
    existing_transactions_growth = load_existing_data('transactions_growth_data.csv')
    existing_general_stats = load_existing_data('general_stats_data.csv', date_key='timestamp')
    
    save_data_to_csv(active_accounts_data, 'active_accounts_data.csv', existing_active_accounts)
    save_data_to_csv(transactions_growth_data, 'transactions_growth_data.csv', existing_transactions_growth, ignore_today=True)
    save_general_stats_to_csv(general_stats_data, 'general_stats_data.csv', existing_general_stats)

    if first_run:
        # Upload entire CSV files for the first run
        print("First run: Uploading entire CSV files to Dune.")
        upload_to_dune('active_accounts_data.csv', dune_user, dune_table_active_accounts)
        upload_to_dune('transactions_growth_data.csv', dune_user, dune_table_transactions_growth)
        upload_to_dune('general_stats_data.csv', dune_user, dune_table_general_stats)
    else:
        # Force creation of temporary CSV for active accounts data even if no new data
        temp_active_accounts_csv = create_temp_csv(active_accounts_data, 'active_accounts_data.csv', ['date', 'value'])
        
        new_transactions_growth_data = [row for row in transactions_growth_data if row['date'] not in existing_transactions_growth]
        new_general_stats_data = [general_stats_data] if general_stats_data['timestamp'] not in existing_general_stats else []

        temp_transactions_growth_csv = create_temp_csv(new_transactions_growth_data, 'transactions_growth_data.csv', ['date', 'value'])
        temp_general_stats_csv = create_temp_csv(new_general_stats_data, 'general_stats_data.csv', [
            'timestamp', 'average_block_time', 'coin_price', 'gas_average', 'gas_fast', 'gas_slow', 
            'gas_used_today', 'market_cap', 'network_utilization_percentage', 'static_gas_price', 
            'total_addresses', 'total_blocks', 'total_gas_used', 'total_transactions', 'transactions_today'
        ])

        # Upload new data to Dune
        print("Subsequent run: Uploading new data to Dune.")
        if temp_active_accounts_csv:
            upload_to_dune(temp_active_accounts_csv, dune_user, dune_table_active_accounts)
        if temp_transactions_growth_csv:
            upload_to_dune(temp_transactions_growth_csv, dune_user, dune_table_transactions_growth)
        if temp_general_stats_csv:
            upload_to_dune(temp_general_stats_csv, dune_user, dune_table_general_stats)

        # Remove temporary CSV files
        if temp_active_accounts_csv:
            os.remove(temp_active_accounts_csv)
        if temp_transactions_growth_csv:
            os.remove(temp_transactions_growth_csv)
        if temp_general_stats_csv:
            os.remove(temp_general_stats_csv)
        print("Temporary CSV files removed.")

if __name__ == "__main__":
    main()