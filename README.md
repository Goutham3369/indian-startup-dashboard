# Indian Startup Funding Analysis Dashboard

This project is an interactive web dashboard built with Streamlit that provides a comprehensive analysis of the Indian startup funding ecosystem from 2015 to 2020. This tool allows users to explore funding trends, identify key players, and derive insights from a complex dataset.


Direct Link for the Site: https://goutham3369-indian-startup-dashboard-dashboard-mprctw.streamlit.app/

## Dashboard Preview



## Features

* **High-Level KPIs:** View key metrics like Total Investment, Number of Startups Funded, and Average Investment amount.
* **Dynamic Filtering:** Interactively filter the entire dataset by Year, Investor, and Industry Vertical.
* **Data Visualizations:**
    * Bar chart for the **Top Funded Sectors**.
    * Pie chart showing the **Funding Distribution by City**.
    * Bar chart for the **Top 10 Most Funded Startups**.
* **Detailed Data Table:** A sortable and searchable table of individual funding deals.

## Tech Stack

* **Language:** Python
* **Data Manipulation:** Pandas
* **Dashboard Framework:** Streamlit
* **Plotting:** Plotly

## How to Run

1.  **Clone the repository:**
   ```bash
git clone https://github.com/Goutham3369/indian-startup-dashboard.git
cd indian-startup-dashboard
   ```

2.  **Create and activate a virtual environment (recommended):**
    ```bash
    # On macOS/Linux
    python3 -m venv venv
    source venv/bin/activate

    # On Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  **Install the required libraries:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the Streamlit app:**
    (Assuming your main Python file is named `app.py`)
    ```bash
    streamlit run app.py
    ```

## Dataset

The dataset used for this project was sourced from Kaggle and contains funding information for Indian startups between 2015 and 2020. The raw data required extensive cleaning and preprocessing to handle inconsistencies in formatting, city names, and numerical values.
