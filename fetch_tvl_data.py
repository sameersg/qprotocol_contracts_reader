import requests
import pandas as pd
from datetime import datetime
import os

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
    token_ids = 'usd-coin,dai,wrapped-bitcoin,elk-finance,vnx-gold,weth,q-protocol'
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

def get_stq_price():
    url = "https://explorer.q.org/api/v2/smart-contracts/0x1CC2f3A24F5c826af7F98A91b98BeC2C05115d01/methods-read-proxy?is_custom_abi=true&from=0xF61f5c4a3664501F499A9289AaEe76a709CE536e"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        for method in data:
            if method.get('method_id') == 'f2f3fea8' and method['name'] == 'getStQPrice':
                return wei_to_token(int(method['outputs'][0]['value']), 18)
    except requests.RequestException as e:
        print(f"Failed to fetch STQ price: {e}")
        return None

wbtc_info = get_token_info("0xde397e6C442A3E697367DecBF0d50733dc916b79")
weth_info = get_token_info("0xd56F9ffF3fe3BD0C7B52afF9A42eb70E05A287Cc")
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

#Infinity 
inf_elk = get_contract_balances("0x1EAf38375CA45685D3FCa0c53e9fa6b02bb9B0D5")
inf_weth = get_contract_balances("0x367750af92a2C427Cc94E1c562DEa9753a42c27e")
inf_usdc = get_contract_balances("0x41AA6785b4ffE18A79bba796793E828059Ff342a")





wbtc_usd_price = prices.get('wrapped-bitcoin', {}).get('usd', 0)
elk_usd_price = prices.get('elk-finance', {}).get('usd', 0)
vnxau_usd_price = prices.get('vnx-gold', {}).get('usd', 0)
weth_usd_price = prices.get('weth', {}).get('usd', 0)
qgov_usd_price = prices.get('q-protocol', {}).get('usd', 0)
stq_price = get_stq_price()

elk_locked_qusd_total = sum([
    elk_locked_wbtc.get('QUSD', 0),
    elk_locked_usdc.get('QUSD', 0),
    elk_locked_dai.get('QUSD', 0),
    elk_locked_elk.get('QUSD', 0),
    elk_locked_vnxau.get('QUSD', 0)
])

bridged_elk = float(elk_info['total_supply']) - float(reservoir_supply_info.get('ELK', 0))

data_row = {
    'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    'btc_in_usd': wbtc_usd_price,
    'elk_in_usd': elk_usd_price,
    'vnxau_in_usd': vnxau_usd_price,
    'weth_in_usd': weth_usd_price,
    'stq_conv_rate': stq_price,
    'bridged_wbtc': wbtc_info['total_supply'],
    'bridged_usdc': usdc_info['total_supply'],
    'bridged_dai': dai_info['total_supply'],
    'bridged_weth': weth_info['total_supply'],
    'bridged_elk': bridged_elk,
    'total_qusd': total_qusd['total_supply'],
    'locked_wbtc': locked_contract_info.get('WBTC', 'Unknown'),
    'locked_usdc': locked_contract_info.get('USDC', 'Unknown'),
    'locked_dai': locked_contract_info.get('DAI', 'Unknown'),
    'saving_tvl': saved_qusd.get('QUSD', 'Unknown'),
    'elk_locked_wbtc': elk_locked_wbtc.get('WBTC', 'Unknown'),
    'elk_locked_usdc': elk_locked_usdc.get('USDC', 'Unknown'),
    'elk_locked_dai': elk_locked_dai.get('DAI', 'Unknown'),
    'elk_locked_elk': elk_locked_elk.get('ELK', 'Unknown'),
    'elk_locked_qusd': elk_locked_qusd_total,
    'elk_locked_vnxau': elk_locked_vnxau.get('VNXAU', 'Unknown'),
    'stq_supply': stQ_meta['total_supply'],
    'extra_1': inf_elk.get('ELK', 'Unknown'),
    'extra_2': inf_weth.get('WETH', 'Unknown'),
    'extra_3': inf_usdc.get('USDC', 'Unknown'),
    'extra_4': qgov_usd_price,
    'extra_5': 0.0,
    'extra_6': 0.0,
    'extra_7': 0.0,
    'extra_8': 0.0,
    'extra_9': 0.0,
    'extra_10': 0.0,
    'extra_11': 0.0,
    'extra_12': 0.0,
    'extra_13': 0.0,
    'extra_14': 0.0,
    'extra_15': 0.0,
    'extra_16': 0.0,
    'extra_17': 0.0,
    'extra_18': 0.0,
    'extra_19': 0.0,
    'extra_20': 0.0
}

new_row = pd.DataFrame([data_row])
csv_file_path = 'token_and_contract_data.csv'
print(f"Attempting to write to CSV at: {os.path.abspath(csv_file_path)}")

# Manually set this flag to True for the first run, then False for subsequent runs
first_run = False
# Define the user and table names for Dune upload
dune_user = ''  # Replace with your Dune user name
dune_table = ''  # Replace with your Dune table name
api = '' # Replace with your Dune api
try:
    if os.path.exists(csv_file_path):
        print("File exists. Reading and appending...")
        df = pd.read_csv(csv_file_path)
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv(csv_file_path, index=False)
        print("Data appended and saved.")
    else:
        print("File does not exist. Creating new file...")
        new_row.to_csv(csv_file_path, index=False)
        print("New file created and data written.")

    df = pd.read_csv(csv_file_path)
    print("Data successfully written. Here's a preview:")
    print(df.tail())
except Exception as e:
    print(f"Error during file operation: {e}")

def upload_to_dune(csv_path, namespace, table_name):
    url = f"https://api.dune.com/api/v1/table/{namespace}/{table_name}/insert"
    headers = {
        "X-DUNE-API-KEY": api,
        "Content-Type": "text/csv"
    }
    with open(csv_path, "rb") as data:
        response = requests.request("POST", url, data=data, headers=headers)
    print(response.text)

if first_run:
    print("First run: Uploading entire CSV.")
    upload_to_dune(csv_file_path, dune_user, dune_table)
else:
    print("Subsequent run: Uploading new data only.")
    temp_csv_path = 'temp_new_data.csv'
    print("Subsequent run: Created tempfile")
    new_row.to_csv(temp_csv_path, index=False)
    upload_to_dune(temp_csv_path, dune_user, dune_table)
    os.remove(temp_csv_path)
    print("Subsequent run: Deleted tempfile")