
import pandas as pd

# --- Step 1: Load the Data ---
# Load the CSV file into a pandas DataFrame (a table)
df = pd.read_csv('startup_funding.csv', encoding='utf-8')


# --- Step 2: Clean the Data (Very Important) ---

df.rename(columns={
    'Date dd/mm/yyyy': 'Date', # Correctly named
    'Startup Name': 'StartupName',
    'Industry Vertical': 'IndustryVertical',
    'City  Location': 'CityLocation', # Corrected: two spaces in original name
    'Amount in USD': 'AmountInUSD' # Correctly named
}, inplace=True)

# Drop rows where essential data is missing
df.dropna(subset=['CityLocation', 'IndustryVertical', 'AmountInUSD', 'Date'], inplace=True)

# Correct city names: unify 'bangalore' and 'Bangalore' into 'Bengaluru'
df['CityLocation'] = df['CityLocation'].str.split('/').str[0].str.strip()
df['CityLocation'] = df['CityLocation'].str.replace('bangalore', 'Bengaluru', case=False)
df['CityLocation'] = df['CityLocation'].str.replace(r'Delhi\b', 'New Delhi', regex=True, case=False)


# Clean the amount column: remove commas, correct specific errors, and convert to numbers
df['AmountInUSD'] = df['AmountInUSD'].astype(str).str.lower()
df['AmountInUSD'].replace(to_replace=['undisclosed', 'unknown', 'n/a'], value='0', inplace=True)
df['AmountInUSD'] = df['AmountInUSD'].str.replace(r'[^\d.]', '', regex=True)
df['AmountInUSD'] = pd.to_numeric(df['AmountInUSD'], errors='coerce')

# Drop rows where the amount is still missing or zero after cleaning
df.dropna(subset=['AmountInUSD'], inplace=True)
df = df[df['AmountInUSD'] > 0]

# Clean the date column and extract the year
df['Date'] = df['Date'].str.replace('.', '/', regex=False).str.replace('//', '/', regex=False)
df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
df.dropna(subset=['Date'], inplace=True) # Drop rows where date conversion failed
df['Year'] = df['Date'].dt.year


# --- Step 3: Perform the Analysis ---

# 1. Overall funding year over year
yearly_funding = df.groupby('Year')['AmountInUSD'].sum().sort_index().astype('int64')

# 2. Top 10 most funded cities
city_funding = df.groupby('CityLocation')['AmountInUSD'].sum().sort_values(ascending=False).head(10)

# 3. Top 10 most funded sectors (industries)
sector_funding = df.groupby('IndustryVertical')['AmountInUSD'].sum().sort_values(ascending=False).head(10)


# --- Step 4: Display the Results ---

print("--- Analysis of Indian Startup Funding ---")

print("\n--- Total Funding Per Year (in USD) ---")
# Format the numbers to be more readable (e.g., with commas)
print(yearly_funding.apply(lambda x: f"{x:,.0f}"))

print("\n--- Top 10 Most Funded Cities (in USD) ---")
print(city_funding.apply(lambda x: f"{x:,.0f}"))

print("\n--- Top 10 Most Funded Sectors (in USD) ---")
print(sector_funding.apply(lambda x: f"{x:,.0f}"))