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
    if "postgres" not in st.secrets:
        st.error("🚨 Missing Database Secrets! Please configure `[postgres]` in `.streamlit/secrets.toml` or Streamlit Cloud Secrets.")
        st.stop()
        
    return psycopg2.connect(
        host=st.secrets["postgres"]["host"],
        port=st.secrets["postgres"]["port"],
        database=st.secrets["postgres"]["dbname"],
        user=st.secrets["postgres"]["user"],
        password=st.secrets["postgres"]["password"]
    )

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
