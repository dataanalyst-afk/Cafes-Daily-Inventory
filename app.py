import streamlit as st
import psycopg2
from datetime import date

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="Daily Closing Stock",
    layout="wide"
)

# -------------------------------------------------
# CUSTOM CSS (Compact UI)
# -------------------------------------------------
st.markdown("""
<style>
.main {
    padding-top: 1rem;
    padding-bottom: 1rem;
}
.block-container {
    padding-top: 1.5rem;
    max-width: 900px;
}
label {
    font-size: 14px !important;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# DATA
# -------------------------------------------------
CATEGORY_ITEMS = {
    "Beverages": ["Cappuccino", "Latte", "Espresso"],
    "Syrups": ["Vanilla Syrup", "Caramel Syrup"],
    "Milk": ["Full Cream Milk", "Almond Milk"],
    "Cups": ["Small Cup", "Medium Cup", "Large Cup"]
}

CAFE_OUTLETS = [
    "Downtown Cafe",
    "Bandra Cafe",
    "Andheri Cafe"
]

# -------------------------------------------------
# DATABASE CONNECTION
# -------------------------------------------------
@st.cache_resource
def get_connection():
    # Try getting secrets first
    if "postgres" in st.secrets:
        try:
            try:
                return psycopg2.connect(
                    host=st.secrets["postgres"]["host"],
                    port=st.secrets["postgres"]["port"],
                    database=st.secrets["postgres"]["dbname"],
                    user=st.secrets["postgres"]["user"],
                    password=st.secrets["postgres"]["password"]
                )
            except psycopg2.OperationalError as e: # Specific handling for OperationalError
                st.error(f"🚨 Database connection failed (OperationalError)! Check host, port, user, password. Error: {e}")
                if "localhost" in st.secrets["postgres"]["host"] or "127.0.0.1" in st.secrets["postgres"]["host"]:
                    st.warning("💡 Hint: You are trying to connect to 'localhost' via Secrets. This works locally but FAILS on Streamlit Cloud. You need a hosted database.")
                st.stop()
        except psycopg2.Error as e: # General psycopg2 error handling
            st.error(f"🚨 Connection Failed! Check your Streamlit Secrets or database configuration. Error: {e}")
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

conn = get_connection()
cursor = conn.cursor()

# -------------------------------------------------
# UI
# -------------------------------------------------
st.title("☕ Daily Closing Stock Entry")

col1, col2 = st.columns(2)

with col1:
    stock_date = st.date_input("Date", value=date.today())
    cafeoutlet = st.selectbox("Cafe Outlet", CAFE_OUTLETS)
    category = st.selectbox("Category", list(CATEGORY_ITEMS.keys()))

with col2:
    item = st.selectbox("Item", CATEGORY_ITEMS[category])
    closing_stock = st.number_input(
        "Closing Stock",
        min_value=0.0,
        step=0.1
    )

st.markdown("###")

# -------------------------------------------------
# SUBMIT
# -------------------------------------------------
if st.button("💾 Save Entry", use_container_width=True):
    cursor.execute(
        """
        INSERT INTO daily_inventory
        (stock_date, category, item_name, closing_stock, cafeoutlet)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (stock_date, category, item, closing_stock, cafeoutlet)
    )
    conn.commit()
    st.success("✅ Closing stock saved successfully")
