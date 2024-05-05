# Cryptocurrency Analytics Platform

This repository contains Python scripts and SQL queries for collecting, processing, and analyzing cryptocurrency data, including minting, burning, and Total Value Locked (TVL) across various tokens and contracts.

## Repository Structure

### Python Scripts

1. **Mint and Burn Processing**
   - `mintandburn.py`: Processes mint and burn events, stores data locally, and uploads to Dune for analysis.

2. **Fetch TVL Data**
   - `fetch_tvl_data.py`: Fetches TVL data from APIs, calculates values, and stores in CSV format.

3. **Dune TVL Table Creation**
   - `dune_create_table.py`: Creates a Dune table to store and analyze TVL data.

### SQL Queries

1. **TVL Analysis**
   - `tvl_analysis.sql`: Analyzes daily and monthly TVL data stored on Dune.

2. **Account Transactions Analysis**
   - `account_transactions_analysis.sql`: Analyzes transaction and account growth rates.

## Installation

1. Clone the repository:
   ```
   git clone 
   ```

2. Install required packages:
   ```
   pip install requests pandas
   ```

## Usage

### Running Python Scripts

Execute scripts individually as needed:
```
python mintandburn.py
python fetch_tvl_data.py
python dune_create_table.py
```

### Executing SQL Queries

Upload SQL files to Dune dashboard or run directly in your SQL client.

## Contributing

Fork the repository and submit pull requests with your changes.

## License

Licensed under the MIT License - see LICENSE.md for details.

## Contact

Open an issue in the repository for any questions.
```

