# QuimQuinAgro Accounting Dashboard (Reto 2)
  
The goal was to create a simple Streamlit dashboard connected to a SQLite database (`contabilidad.db`) to visualize QuimQuinAgro’s financial information using predefined SQL queries.

## Implemented Queries
1. **Monthly Cash Flow (Q1)** – Shows total income and expenses per month.  
2. **Top 10 Expenses (Q2)** – Displays the ten largest outflows by transaction detail.  
3. **Income by Partner (Q3)** – Calculates total income per partner.

## How to Run the App
1. Open **Anaconda Navigator** and launch Anaconda Prompt . 
2. Navigate to the folder where the project files (`app.py` and `contabilidad.db`) are located.  (I saved these in a new folder on my desktop to facilitate the process)
3. Make sure the required libraries are installed (pip install streamlit pandas altair)
4. Once installed, start the Streamlit app by typing: streamlit run app.py
5. The dashboard will open automatically in your browser, where you can interact with the SQL queries and filters.
