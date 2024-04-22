import requests
import pandas as pd
from datetime import datetime
import os

def wei_to_ether(wei_value):
    return float(wei_value) / 10**18

def wei_to_token(wei_value, decimals):
    return float(wei_value) / (10 ** decimals)

def fetch_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return {}

def fetch_prices():
    token_ids = 'usd-coin,dai,wrapped-bitcoin,elk-finance,vnx-gold'
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={token_ids}&vs_currencies=usd"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Failed to fetch prices: {e}")
        return {}

def get_token_info(address):
    data = fetch_data(f"https://explorer.q.org/api/v2/tokens/{address}")
    return {
        'name': data.get('name', 'Unknown'),
        'total_supply': wei_to_token(data.get('total_supply', 0), int(data.get('decimals', 0))) if data.get('total_supply') else 'Unknown'
    }

def get_contract_balances(address):
    data = fetch_data(f"https://explorer.q.org/api/v2/addresses/{address}/token-balances")
    balances = {}
    for token in data:
        balances[token['token']['symbol']] = wei_to_token(token['value'], int(token['token']['decimals']))
    return balances

prices = fetch_prices()

# Define the columns for your DataFrame
columns = ['Date', 'BTC in USD', 'ELK in USD', 'VNXAU in USD', 'Bridged WBTC', 'Bridged USDC',
           'Bridged DAI', 'Bridged ELK', 'Bridged USD Value', 'Total QUSD', 'Locked WBTC', 'Locked USDC',
           'Locked DAI', 'Borrowing TVL', 'Saving TVL', 'Elk Locked WBTC', 'Elk Locked USDC', 'Elk Locked DAI',
           'Elk Locked Elk', 'Elk Locked QUSD', 'Elk Locked VNXAU', 'Elk TVL', 'stQ Supply',
           'Total TVL']

df = pd.DataFrame(columns=columns)

# Collect data for bridged assets
wbtc_info = get_token_info("0xde397e6C442A3E697367DecBF0d50733dc916b79")
usdc_info = get_token_info("0x79Cb92a2806BF4f82B614A84b6805963b8b1D8BB")
dai_info = get_token_info("0xDeb87c37Dcf7F5197026f574cd40B3Fc8Aa126D1")
elk_info = get_token_info("0xeEeEEb57642040bE42185f49C52F7E9B38f8eeeE")
stQ_meta = get_token_info("0x1CC2f3A24F5c826af7F98A91b98BeC2C05115d01")
reservoir_supply_info = get_contract_balances("0x42424242B0c0d8A19dCD0dF362815E242586354A")
locked_contract_info = get_contract_balances("0xb9c29d9A24B233C53020891D47F82043da615Dcc")
total_qusd = get_token_info("0xE31DD093A2A0aDc80053bF2b929E56aBFE1B1632")
saved_qusd = get_contract_balances("0x7CCa96c630329c1972547e95B9f3F82eC31A916A")
elk_locked_wbtc = get_contract_balances("0x38d54a9a8C622CD682398C2Bef7341D08b32e4b1")
elk_locked_usdc = get_contract_balances("0x2A36b45be4C04900A5946A1B6bf991aDec93ADdE")
elk_locked_dai = get_contract_balances("0x566989560917879868cb98C5EF72d9050298c49c")
elk_locked_elk = get_contract_balances("0x8490a1ece0363dE138d39022629785e060422571")
elk_locked_vnxau = get_contract_balances("0x4300B43659e2d4300FF9379Db65cBFb036Ab9096")

wbtc_usd_price = prices.get('wrapped-bitcoin', {}).get('usd', 0)
elk_usd_price = prices.get('elk-finance', {}).get('usd', 0)

# Calculate totals and values
elk_locked_qusd_total = sum([
    elk_locked_wbtc.get('QUSD', 0),
    elk_locked_usdc.get('QUSD', 0),
    elk_locked_dai.get('QUSD', 0),
    elk_locked_elk.get('QUSD', 0),
    elk_locked_vnxau.get('QUSD', 0)
])
bridged_elk = float(elk_info['total_supply']) - float(reservoir_supply_info.get('ELK', 0))
elk_usd_value = elk_locked_wbtc.get('WBTC', 'Unknown') * wbtc_usd_price + \
                usdc_info['total_supply'] * 1 + \
                dai_info['total_supply'] * 1 + \
                bridged_elk * elk_usd_price
bridged_usd_value = wbtc_info['total_supply'] * wbtc_usd_price + \
                    elk_locked_usdc.get('USDC', 'Unknown') * 1 + \
                    elk_locked_dai.get('DAI', 'Unknown') * 1 + \
                    elk_locked_qusd_total + \
                    elk_locked_elk.get('ELK', 'Unknown') * elk_usd_price
borrowing_tvl = locked_contract_info.get('WBTC', 0) * wbtc_usd_price + \
                locked_contract_info.get('USDC', 0) + \
                locked_contract_info.get('DAI', 0)
total_tvl = borrowing_tvl + \
            saved_qusd.get('QUSD', 'Unknown') + \
            elk_usd_value


# Prepare and format data row for DataFrame
data_row = {
    'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    'btc_in_usd': wbtc_usd_price,
    'elk_in_usd': elk_usd_price,
    'vnxau_in_usd': prices.get("vnx-gold", {}).get('usd', 'N/A'),
    'bridged_wbtc': wbtc_info['total_supply'],
    'bridged_usdc': usdc_info['total_supply'],
    'bridged_dai': dai_info['total_supply'],
    'bridged_elk': bridged_elk,
    'bridged_usd_value': bridged_usd_value,
    'total_qusd': total_qusd['total_supply'],
    'locked_wbtc': locked_contract_info.get('WBTC', 'Unknown'),
    'locked_usdc': locked_contract_info.get('USDC', 'Unknown'),
    'locked_dai': locked_contract_info.get('DAI', 'Unknown'),
    'borrowing_tvl': borrowing_tvl,
    'saving_tvl': saved_qusd.get('QUSD', 'Unknown'),
    'elk_locked_wbtc': elk_locked_wbtc.get('WBTC', 'Unknown'),
    'elk_locked_usdc': elk_locked_usdc.get('USDC', 'Unknown'),
    'elk_locked_dai': elk_locked_dai.get('DAI', 'Unknown'),
    'elk_locked_elk': elk_locked_elk.get('ELK', 'Unknown'),
    'elk_locked_qusd': elk_locked_qusd_total,
    'elk_locked_vnxau': elk_locked_vnxau.get('VNXAU', 'Unknown'),
    'elk_tvl': elk_usd_value,
    'stq_supply': stQ_meta['total_supply'],
    'total_tvl': total_tvl
}


# Convert the dictionary to a DataFrame
new_row = pd.DataFrame([data_row])

# Path to the CSV file
csv_file_path = 'token_and_contract_data.csv'

# Check if the file exists to append or create new
if os.path.exists(csv_file_path):
    df = pd.read_csv(csv_file_path)
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(csv_file_path, index=False)
else:
    new_row.to_csv(csv_file_path, index=False)

# Read and display to verify
df = pd.read_csv(csv_file_path)
print(df)

# Dune upload part
def upload_to_dune(csv_path, namespace, table_name):
    url = f"https://api.dune.com/api/v1/table/{username}/{tablename}/insert"
    headers = {
        "X-DUNE-API-KEY": "",
        "Content-Type": "text/csv"
    }
    with open(csv_path, "rb") as data:
        response = requests.request("POST", url, data=data, headers=headers)
    print(response.text)

# Call the upload function
upload_to_dune(csv_file_path, 'my_user', 'my_table')
