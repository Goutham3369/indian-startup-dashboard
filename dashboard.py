import streamlit as st
import pandas as pd
import plotly.express as px

# Set the page configuration for the dashboard - this must be the first Streamlit command
st.set_page_config(layout="wide", page_title="Indian Startup Funding Analysis")

# --- Helper Function for Indian Currency Formatting ---
def format_indian_currency(n):
    """Formats a number into the Indian Lakhs and Crores comma style."""
    if not isinstance(n, (int, float)):
        return n
    n = int(n)
    s = str(n)
    if len(s) < 4:
        return '₹' + s
    last_three = s[-3:]
    rest = s[:-3]
    formatted_rest = ""
    while len(rest) > 2:
        formatted_rest = "," + rest[-2:] + formatted_rest
        rest = rest[:-2]
    return '₹' + rest + formatted_rest + "," + last_three

# --- Data Loading and Cleaning Function ---
@st.cache_data
def load_data():
    """This function loads, cleans, and prepares the startup funding data."""
    df = pd.read_csv('startup_funding.csv', encoding='utf-8')


    df.rename(columns={
        'Date dd/mm/yyyy': 'Date',
        'Startup Name': 'StartupName',
        'Industry Vertical': 'IndustryVertical',
        'City  Location': 'CityLocation',
        'CityLocation': 'CityLocation',
        'Investors Name': 'InvestorsName',
        'Amount in USD': 'AmountInUSD'
    }, inplace=True)

    text_columns = ['StartupName', 'IndustryVertical', 'CityLocation', 'InvestorsName']
    for col in text_columns:
        if col in df.columns:
            df[col] = df[col].astype(str).str.encode('ascii', 'ignore').str.decode('utf-8')
            df[col] = df[col].str.replace(r'\\x[0-9a-fA-F]{2}', '', regex=True)
            df[col] = df[col].str.replace(r'\\', '', regex=True).str.replace('"', '').str.strip()

    # Drop rows with missing essential data
    df.dropna(subset=['CityLocation', 'IndustryVertical', 'AmountInUSD', 'Date', 'StartupName'], inplace=True)

    # Robust city name cleaning
    df['CityLocation'] = df['CityLocation'].str.split('/').str[0].str.strip()
    df['CityLocation'] = df['CityLocation'].str.replace('bangalore', 'Bengaluru', case=False)
    df['CityLocation'] = df['CityLocation'].str.replace('gurgaon', 'Gurugram', case=False)
    df.loc[df['CityLocation'] == 'Delhi', 'CityLocation'] = 'New Delhi'

    # Replace missing investor names
    df['InvestorsName'].fillna('Undisclosed', inplace=True)

    # Clean the amount column
    df['AmountInUSD'] = df['AmountInUSD'].astype(str).str.lower().replace(to_replace=['undisclosed', 'unknown', 'n/a'], value='0')
    df['AmountInUSD'] = df['AmountInUSD'].str.replace(r'[^\d.]', '', regex=True)
    df['AmountInUSD'] = pd.to_numeric(df['AmountInUSD'], errors='coerce')
    df.dropna(subset=['AmountInUSD'], inplace=True)
    df = df[df['AmountInUSD'] > 0]

    # Clean the date column
    df['Date'] = df['Date'].str.replace('.', '/', regex=False).str.replace('//', '/', regex=False)
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
    df.dropna(subset=['Date'], inplace=True)
    df['Year'] = df['Date'].dt.year
    
    # Add the INR conversion column
    USD_TO_INR = 83 # Using a static conversion rate for September 2025
    df['AmountInINR'] = df['AmountInUSD'] * USD_TO_INR
    
    return df

df = load_data()

# --- SIDEBAR and FILTERS ---
st.sidebar.title("Filters")
st.sidebar.info("Note: This dashboard uses a historical dataset with funding data up to 2020.")

selected_currency = st.sidebar.radio("Select Currency", ["USD", "INR"])

year_list = ['Overall'] + sorted(df['Year'].dropna().astype(int).unique(), reverse=True)
selected_year = st.sidebar.selectbox("Select Year", year_list)
if selected_year == 'Overall':
    temp_df_year = df.copy()
else:
    temp_df_year = df[df['Year'] == int(selected_year)]

investor_list = ['Overall'] + sorted(temp_df_year['InvestorsName'].dropna().unique())
selected_investor = st.sidebar.selectbox("Select Investor", investor_list)
if selected_investor == 'Overall':
    temp_df_investor = temp_df_year.copy()
else:
    temp_df_investor = temp_df_year[temp_df_year['InvestorsName'].str.contains(selected_investor, na=False)]

sector_list = ['Overall'] + sorted(temp_df_investor['IndustryVertical'].dropna().unique())
selected_sector = st.sidebar.selectbox("Select Sector", sector_list)
if selected_sector == 'Overall':
    filtered_df = temp_df_investor.copy()
else:
    filtered_df = temp_df_investor[temp_df_investor['IndustryVertical'] == selected_sector]


# --- MAIN PAGE ---
st.title("Indian Startup Funding Dashboard")
st.header(f"Displaying Results for: {selected_year} (Year), {selected_investor} (Investor), & {selected_sector} (Sector)")

if filtered_df.empty:
    st.warning("No data available for the selected filters.")
else:
    # Dynamic Currency Logic for all calculations
    if selected_currency == 'INR':
        amount_col = 'AmountInINR'
        currency_label = 'Total Funding (INR)'
        total_investment = format_indian_currency(filtered_df[amount_col].sum())
        avg_investment_raw = filtered_df.groupby('StartupName')[amount_col].sum().mean()
        avg_investment = format_indian_currency(avg_investment_raw)
    else: # USD
        amount_col = 'AmountInUSD'
        currency_label = 'Total Funding (USD)'
        total_investment_raw = filtered_df[amount_col].sum()
        total_investment = f"${round(total_investment_raw / 1000000000, 2)}B"
        avg_investment_raw = filtered_df.groupby('StartupName')[amount_col].sum().mean()
        avg_investment = f"${round(avg_investment_raw / 1000000, 2)}M"

    num_startups = filtered_df['StartupName'].nunique()
        
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Investment", total_investment)
    with col2:
        st.metric("Number of Startups", num_startups)
    with col3:
        st.metric("Average Investment", avg_investment)
        
    st.markdown("---")
    
    # DYNAMIC CHARTS
    col1, col2 = st.columns(2)
    with col1:
        st.header("Top Funded Sectors")
        sector_funding = filtered_df.groupby('IndustryVertical')[amount_col].sum().sort_values(ascending=False).head(10)
        fig_sector = px.bar(sector_funding, y=sector_funding.index, x=amount_col, orientation='h', labels={'x': currency_label, 'IndustryVertical': 'Sector'})
        st.plotly_chart(fig_sector, use_container_width=True)
    with col2:
        st.header("Top Funded Cities")
        city_funding = filtered_df.groupby('CityLocation')[amount_col].sum().sort_values(ascending=False).head(10)
        fig_city = px.pie(city_funding, names=city_funding.index, values=amount_col, title='Funding Distribution by City')
        st.plotly_chart(fig_city, use_container_width=True)
        
    st.header("Top 10 Most Funded Startups")
    startup_funding = filtered_df.groupby('StartupName')[amount_col].sum().sort_values(ascending=False).head(10)
    fig_startup = px.bar(startup_funding, x=startup_funding.index, y=amount_col, labels={'y': currency_label, 'StartupName': 'Startup'})
    st.plotly_chart(fig_startup, use_container_width=True)
    
    # DYNAMIC FINAL TABLE
    if selected_year == 'Overall' and selected_investor == 'Overall' and selected_sector == 'Overall':
        st.header("All Funding Deals (Sorted by Most Recent)")
        detail_table = filtered_df.sort_values(by='Date', ascending=False)
    else:
        st.header("Top 20 Funding Deals")
        detail_table = filtered_df.sort_values(by='Date', ascending=False).head(20)

    # Format table based on selected currency
    if selected_currency == 'INR':
        display_columns = ['Date', 'StartupName', 'IndustryVertical', 'CityLocation', 'InvestorsName', 'AmountInINR']
        detail_table_display = detail_table[display_columns].copy()
        detail_table_display['AmountInINR'] = detail_table_display['AmountInINR'].apply(format_indian_currency)
        detail_table_display.rename(columns={'AmountInINR': 'Amount (INR)'}, inplace=True)
    else: # USD
        display_columns = ['Date', 'StartupName', 'IndustryVertical', 'CityLocation', 'InvestorsName', 'AmountInUSD']
        detail_table_display = detail_table[display_columns].copy()
        detail_table_display['AmountInUSD'] = detail_table_display['AmountInUSD'].apply(lambda x: f"${x:,.0f}")
        detail_table_display.rename(columns={'AmountInUSD': 'Amount (USD)'}, inplace=True)

    detail_table_display['Date'] = detail_table_display['Date'].dt.strftime('%d-%b-%Y')
    detail_table_display.rename(columns={'Date': 'Funding Date'}, inplace=True)
    detail_table_display.reset_index(drop=True, inplace=True)
    st.dataframe(detail_table_display, use_container_width=True)
