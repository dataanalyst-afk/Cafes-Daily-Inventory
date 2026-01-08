import streamlit as st
import psycopg2
import pandas as pd
from datetime import date

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="Cafe Inventory System",
    layout="wide"
)

# -------------------------------------------------
# CUSTOM CSS
# -------------------------------------------------
st.markdown("""
<style>
.main { padding-top: 1rem; }
.block-container { max-width: 900px; }
label { font-size: 14px !important; }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# MASTER DATA
# -------------------------------------------------
CATEGORY_ITEMS = {
    "Cookies and Food": [
        "Fudgy Pecan Cookies 50gms (72% Dark Chocolate)",
        "Vegan cranberry cookie",
        "Hazelnut brown butter cookie",
        "Dominican dark cookie",
        "Orange and poppy seed cookie",
        "Berry Good Bark (80gm)",
        "Pistachio Biscotti",
        "Spiced Biscotti",
        "Coffee protein bit"
    ],
    "Single Serve Pour Over Bags": ["Cappuccino", "Latte", "Espresso"],
    "Syrups": ["Vanilla Syrup", "Caramel Syrup"],
    "Milk": ["Full Cream Milk", "Almond Milk"],
    "Cups": ["Small Cup", "Medium Cup", "Large Cup"]
}

CAFE_OUTLETS = ["Downtown Cafe", "Bandra Cafe", "Andheri Cafe"]

# -------------------------------------------------
# DB CONNECTION (SAFE)
# -------------------------------------------------
@st.cache_resource
def get_connection():
    # Try getting secrets first
    if "postgres" in st.secrets:
        try:
            return psycopg2.connect(
                host=st.secrets["postgres"]["host"],
                port=st.secrets["postgres"]["port"],
                database=st.secrets["postgres"]["dbname"],
                user=st.secrets["postgres"]["user"],
                password=st.secrets["postgres"]["password"]
            )
        except psycopg2.Error as e:
            st.error(f"🚨 Connection Failed! Check your Streamlit Secrets. Error: {e}")
            st.stop()
    
    # Fallback to local default credentials
    try:
        return psycopg2.connect(
            host="localhost",
            database="dummy_db",
            user="postgres",
            password="root@1234",
            port="5432"
        )
    except psycopg2.OperationalError as e:
        st.error(f"🚨 Connection Failed! You are running continuously without secrets, so I tried connecting to `localhost` but failed. Error: {e}")
        st.info("ℹ️ If you are on Streamlit Cloud, you MUST configure `.streamlit/secrets.toml` or the Secrets dashboard.")
        st.stop()

def run_query(query, params=None, fetch=False):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(query, params)
        if fetch:
            return cur.fetchall()
        conn.commit()

# -------------------------------------------------
# SIDEBAR
# -------------------------------------------------
page = st.sidebar.radio(
    "📋 Select Page",
    ["Opening Stock", "Daily Inventory", "Daily Report", "Cafe Report", "Item Report"]
)

# =================================================
# OPENING STOCK
# =================================================
if page == "Opening Stock":
    st.title("🌅 Opening Stock Entry")

    col1, col2 = st.columns(2)
    with col1:
        stock_date = st.date_input("Date", value=date.today())
        cafeoutlet = st.selectbox("Cafe Outlet", CAFE_OUTLETS)
        category = st.selectbox("Category", CATEGORY_ITEMS.keys())

    with col2:
        item = st.selectbox("Item", CATEGORY_ITEMS[category])
        opening_stock = st.number_input("Opening Stock", min_value=0.0, step=0.1)

    if st.button("💾 Save Opening Stock", use_container_width=True):
        run_query(
            """
            INSERT INTO opening_stock
            (stock_date, category, item_name, opening_stock, cafeoutlet)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (stock_date, category, item, opening_stock, cafeoutlet)
        )
        st.success("✅ Opening stock saved")

# =================================================
# DAILY INVENTORY
# =================================================
if page == "Daily Inventory":
    st.title("🌙 Daily Inventory Entry")

    col1, col2 = st.columns(2)
    with col1:
        stock_date = st.date_input("Date", value=date.today())
        cafeoutlet = st.selectbox("Cafe Outlet", CAFE_OUTLETS)
        category = st.selectbox("Category", CATEGORY_ITEMS.keys())

    with col2:
        item = st.selectbox("Item", CATEGORY_ITEMS[category])
        closing_stock = st.number_input("Closing Stock", min_value=0.0, step=0.1)

    if st.button("💾 Save Daily Inventory", use_container_width=True):
        run_query(
            """
            INSERT INTO daily_inventory
            (stock_date, category, item_name, closing_stock, cafeoutlet)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (stock_date, category, item, closing_stock, cafeoutlet)
        )
        st.success("✅ Daily inventory saved")

# =================================================
# DAILY REPORT
# =================================================
if page == "Daily Report":
    st.title("📅 Daily Stock Report")
    report_date = st.date_input("Select Date", value=date.today())

    if st.button("🔍 Fetch Report"):
        data = run_query(
            """
            SELECT cafeoutlet, category, item_name, closing_stock, stock_date
            FROM daily_inventory
            WHERE stock_date = %s
            ORDER BY cafeoutlet, category, item_name
            """,
            (report_date,),
            fetch=True
        )

        if data:
            df = pd.DataFrame(data, columns=["Cafe", "Category", "Item", "Closing Stock", "Date"])
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No data found")

# =================================================
# CAFE REPORT
# =================================================
if page == "Cafe Report":
    st.title("🏪 Cafe Stock Report")

    cafe = st.selectbox("Select Cafe", CAFE_OUTLETS)
    start = st.date_input("Start Date", value=date.today())
    end = st.date_input("End Date", value=date.today())

    if st.button("🔍 Fetch Cafe Report"):
        data = run_query(
            """
            SELECT stock_date, category, item_name, closing_stock
            FROM daily_inventory
            WHERE cafeoutlet = %s AND stock_date BETWEEN %s AND %s
            ORDER BY stock_date DESC
            """,
            (cafe, start, end),
            fetch=True
        )

        if data:
            df = pd.DataFrame(data, columns=["Date", "Category", "Item", "Closing Stock"])
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No data found")

# =================================================
# ITEM REPORT
# =================================================
if page == "Item Report":
    st.title("📦 Item Stock Report")

    category = st.selectbox("Category", CATEGORY_ITEMS.keys())
    item = st.selectbox("Item", CATEGORY_ITEMS[category])
    start = st.date_input("From Date", value=date.today())
    end = st.date_input("To Date", value=date.today())

    if st.button("🔍 Fetch Item Report"):
        data = run_query(
            """
            SELECT stock_date, cafeoutlet, closing_stock
            FROM daily_inventory
            WHERE item_name = %s AND stock_date BETWEEN %s AND %s
            ORDER BY stock_date DESC
            """,
            (item, start, end),
            fetch=True
        )

        if data:
            df = pd.DataFrame(data, columns=["Date", "Cafe", "Closing Stock"])
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No data found")
