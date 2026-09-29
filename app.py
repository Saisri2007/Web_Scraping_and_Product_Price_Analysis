
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from pathlib import Path

st.set_page_config(
    page_title="PriceScout | Product Comparison",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_FILE = Path(__file__).parent / "Web_Scraping_Product_Price_Dataset.xlsx"

@st.cache_data
def load_data():
    df = pd.read_excel(DATA_FILE, sheet_name="Product_Data")
    df["Scraped_Date"] = pd.to_datetime(df["Scraped_Date"], errors="coerce")
    for col in ["Price_INR", "Original_Price_INR", "Rating", "Reviews_Count", "Discount_Percent"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df

df = load_data()

def money(v):
    return f"₹{v:,.0f}"

# ---------- Styling ----------
st.markdown("""
<style>
    .stApp { background: #f6f8fc; }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f1f3d 0%, #162b55 100%);
    }
    [data-testid="stSidebar"] * { color: #f4f7ff !important; }
    [data-testid="stSidebar"] input {
    color: black !important;
    -webkit-text-fill-color: black !important;
    }

    [data-testid="stSidebar"] input::placeholder {
        color: #64748b !important;
        -webkit-text-fill-color: #64748b !important;
    }
    .hero {
        padding: 26px 30px;
        border-radius: 20px;
        background: linear-gradient(135deg, #102a56 0%, #2563eb 55%, #60a5fa 100%);
        color: white;
        margin-bottom: 18px;
        box-shadow: 0 10px 30px rgba(37,99,235,.18);
    }
    .hero h1 { margin: 0; font-size: 34px; }
    .hero p { margin: 7px 0 0; opacity: .9; font-size: 16px; }
    .metric {
        background: white;
        border: 1px solid #e7ebf3;
        border-radius: 16px;
        padding: 15px 18px;
        box-shadow: 0 4px 16px rgba(15,23,42,.05);
    }
    .metric-label { color: #64748b; font-size: 13px; }
    .metric-value { color: #0f172a; font-size: 25px; font-weight: 750; margin-top: 2px; }
    .product-card {
        background: white;
        border: 1px solid #e5eaf2;
        border-radius: 16px;
        padding: 16px;
        min-height: 210px;
        box-shadow: 0 5px 18px rgba(15,23,42,.05);
        margin-bottom: 10px;
    }
    .product-name { font-size: 17px; font-weight: 700; color: #0f172a; }
    .store { color: #2563eb; font-weight: 650; font-size: 13px; }
    .price { font-size: 25px; font-weight: 800; color: #111827; }
    .old-price { color: #94a3b8; text-decoration: line-through; font-size: 13px; }
    .badge {
        display: inline-block; padding: 4px 9px; border-radius: 999px;
        background: #ecfdf5; color: #047857; font-size: 12px; font-weight: 650;
        margin-right: 5px;
    }
    .rating { color: #f59e0b; font-weight: 700; }
    .section-title { font-size: 22px; font-weight: 750; color: #0f172a; margin: 18px 0 10px; }
    .small-note { color:#64748b; font-size:12px; }
    div[data-testid="stDataFrame"] { border-radius: 14px; overflow: hidden; }
</style>
""", unsafe_allow_html=True)

# ---------- Header ----------
st.markdown("""
<div class="hero">
    <h1>🛍️ PriceScout</h1>
    <p>Search products, compare stores, filter by price & rating, and explore market insights.</p>
</div>
""", unsafe_allow_html=True)

# ---------- Sidebar filters ----------
st.sidebar.markdown("## 🔎 Search & Filters")
search = st.sidebar.text_input(
    "Search product",
    placeholder="e.g. iPhone, laptop, headphones..."
)

categories = st.sidebar.multiselect(
    "Category",
    options=sorted(df["Category"].dropna().unique()),
)
stores = st.sidebar.multiselect(
    "Store",
    options=sorted(df["Store"].dropna().unique()),
)
availability = st.sidebar.multiselect(
    "Availability",
    options=sorted(df["Availability"].dropna().unique()),
)

price_min, price_max = int(df["Price_INR"].min()), int(df["Price_INR"].max())
price_range = st.sidebar.slider(
    "Price range (₹)",
    min_value=price_min,
    max_value=price_max,
    value=(price_min, price_max),
    step=100,
)

rating_range = st.sidebar.slider(
    "Minimum / maximum rating",
    min_value=float(df["Rating"].min()),
    max_value=float(df["Rating"].max()),
    value=(float(df["Rating"].min()), float(df["Rating"].max())),
    step=0.1,
)

discount_range = st.sidebar.slider(
    "Discount (%)",
    min_value=int(df["Discount_Percent"].min()),
    max_value=int(df["Discount_Percent"].max()),
    value=(int(df["Discount_Percent"].min()), int(df["Discount_Percent"].max())),
)

sort_by = st.sidebar.selectbox(
    "Sort products by",
    ["Relevance", "Price: Low to High", "Price: High to Low",
     "Rating: High to Low", "Discount: High to Low", "Reviews: High to Low"]
)

# ---------- Filtering ----------
filtered = df.copy()

if search.strip():
    q = search.strip().lower()
    mask = (
        filtered["Product_Name"].fillna("").str.lower().str.contains(q, regex=False)
        | filtered["Category"].fillna("").str.lower().str.contains(q, regex=False)
        | filtered["Store"].fillna("").str.lower().str.contains(q, regex=False)
    )
    filtered = filtered[mask]

if categories:
    filtered = filtered[filtered["Category"].isin(categories)]
if stores:
    filtered = filtered[filtered["Store"].isin(stores)]
if availability:
    filtered = filtered[filtered["Availability"].isin(availability)]

filtered = filtered[
    filtered["Price_INR"].between(price_range[0], price_range[1])
    & filtered["Rating"].between(rating_range[0], rating_range[1])
    & filtered["Discount_Percent"].between(discount_range[0], discount_range[1])
]

if sort_by == "Price: Low to High":
    filtered = filtered.sort_values("Price_INR")
elif sort_by == "Price: High to Low":
    filtered = filtered.sort_values("Price_INR", ascending=False)
elif sort_by == "Rating: High to Low":
    filtered = filtered.sort_values(["Rating", "Reviews_Count"], ascending=[False, False])
elif sort_by == "Discount: High to Low":
    filtered = filtered.sort_values("Discount_Percent", ascending=False)
elif sort_by == "Reviews: High to Low":
    filtered = filtered.sort_values("Reviews_Count", ascending=False)

# ---------- KPI row ----------
c1, c2, c3, c4, c5 = st.columns(5)
metrics = [
    ("Products Found", f"{len(filtered):,}"),
    ("Lowest Price", money(filtered["Price_INR"].min()) if len(filtered) else "—"),
    ("Average Price", money(filtered["Price_INR"].mean()) if len(filtered) else "—"),
    ("Avg Rating", f'{filtered["Rating"].mean():.1f} ★' if len(filtered) else "—"),
    ("Avg Discount", f'{filtered["Discount_Percent"].mean():.0f}%' if len(filtered) else "—"),
]
for col, (label, value) in zip([c1,c2,c3,c4,c5], metrics):
    with col:
        st.markdown(
            f'<div class="metric"><div class="metric-label">{label}</div>'
            f'<div class="metric-value">{value}</div></div>',
            unsafe_allow_html=True
        )

# ---------- Results ----------
st.markdown('<div class="section-title">🛒 Product Results</div>', unsafe_allow_html=True)

if filtered.empty:
    st.warning("No products match the current filters. Try widening the price/rating range or clearing a filter.")
else:
    view = st.radio("View", ["Product Cards", "Table"], horizontal=True, label_visibility="collapsed")

    if view == "Product Cards":
        show_df = filtered.head(60)
        for start in range(0, len(show_df), 3):
            cols = st.columns(3)
            for col, (_, row) in zip(cols, show_df.iloc[start:start+3].iterrows()):
                with col:
                    availability_badge = (
                        "In Stock" if row["Availability"] == "In Stock"
                        else row["Availability"]
                    )
                    st.markdown(f"""
                    <div class="product-card">
                        <div class="store">{row["Store"]} · {row["Category"]}</div>
                        <div class="product-name">{row["Product_Name"]}</div>
                        <div style="margin-top:12px;">
                            <span class="price">{money(row["Price_INR"])}</span>
                            <span class="old-price">{money(row["Original_Price_INR"])}</span>
                        </div>
                        <div style="margin-top:8px;">
                            <span class="badge">{row["Discount_Percent"]:.0f}% OFF</span>
                            <span class="badge">{availability_badge}</span>
                        </div>
                        <div style="margin-top:10px;">
                            <span class="rating">★ {row["Rating"]:.1f}</span>
                            <span class="small-note"> · {int(row["Reviews_Count"]):,} reviews</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.link_button("View product", str(row["Product_Link"]), use_container_width=True)
    else:
        table = filtered[[
            "Product_Name", "Category", "Store", "Price_INR", "Original_Price_INR",
            "Discount_Percent", "Rating", "Reviews_Count", "Availability", "Product_Link"
        ]].copy()
        table.columns = [
            "Product", "Category", "Store", "Price (₹)", "Original Price (₹)",
            "Discount (%)", "Rating", "Reviews", "Availability", "Product Link"
        ]
        st.dataframe(
            table,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Price (₹)": st.column_config.NumberColumn(format="₹%d"),
                "Original Price (₹)": st.column_config.NumberColumn(format="₹%d"),
                "Rating": st.column_config.NumberColumn(format="%.1f ★"),
                "Discount (%)": st.column_config.NumberColumn(format="%.0f%%"),
                "Product Link": st.column_config.LinkColumn(display_text="Open"),
            }
        )

# ---------- Compare ----------
st.markdown('<div class="section-title">⚖️ Compare Products</div>', unsafe_allow_html=True)
compare_pool = filtered.head(100)
compare_names = compare_pool["Product_Name"].tolist()

if compare_names:
    selected = st.multiselect(
        "Select up to 4 products",
        compare_names,
        max_selections=4,
        placeholder="Choose products to compare..."
    )
    if selected:
        comp = compare_pool[compare_pool["Product_Name"].isin(selected)].copy()
        comp = comp.sort_values("Price_INR")
        display = comp[[
            "Product_Name", "Store", "Price_INR", "Rating",
            "Discount_Percent", "Reviews_Count", "Availability"
        ]].copy()
        display.columns = ["Product", "Store", "Price (₹)", "Rating", "Discount (%)", "Reviews", "Availability"]
        st.dataframe(display, use_container_width=True, hide_index=True)

# ---------- Analytics ----------
st.markdown('<div class="section-title">📊 Market Analytics</div>', unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs([
    "Price by Store", "Rating vs Price", "Categories", "Discounts"
])

with tab1:
    store_stats = filtered.groupby("Store", as_index=False)["Price_INR"].mean().sort_values("Price_INR")
    fig = px.bar(
        store_stats, x="Store", y="Price_INR",
        title="Average Product Price by Store",
        labels={"Price_INR": "Average price (₹)", "Store": "Store"},
        text_auto=".0f"
    )
    fig.update_layout(template="plotly_white", height=430)
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    scatter = filtered.copy()
    fig = px.scatter(
        scatter, x="Price_INR", y="Rating",
        size="Reviews_Count", color="Category",
        hover_name="Product_Name",
        hover_data=["Store", "Discount_Percent"],
        title="Price vs Customer Rating",
        labels={"Price_INR": "Price (₹)", "Rating": "Rating"}
    )
    fig.update_layout(template="plotly_white", height=430)
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    cat_stats = filtered.groupby("Category", as_index=False).agg(
        Products=("Product_ID", "count"),
        Avg_Price=("Price_INR", "mean"),
        Avg_Rating=("Rating", "mean")
    ).sort_values("Products", ascending=False)
    fig = px.bar(
        cat_stats, x="Category", y="Products",
        title="Products Available by Category",
        labels={"Products": "Number of products", "Category": "Category"},
        text_auto=True
    )
    fig.update_layout(template="plotly_white", height=430, xaxis_tickangle=-30)
    st.plotly_chart(fig, use_container_width=True)

with tab4:
    discount_bins = pd.cut(
        filtered["Discount_Percent"],
        bins=[0, 10, 20, 30, 40],
        labels=["0–10%", "11–20%", "21–30%", "31–40%"],
        include_lowest=True
    )
    discount_counts = discount_bins.value_counts().sort_index().reset_index()
    discount_counts.columns = ["Discount Range", "Products"]
    fig = px.pie(
        discount_counts, names="Discount Range", values="Products",
        title="Discount Distribution"
    )
    fig.update_layout(template="plotly_white", height=430)
    st.plotly_chart(fig, use_container_width=True)

# ---------- Download ----------
st.markdown('<div class="section-title">⬇️ Export</div>', unsafe_allow_html=True)
csv = filtered.to_csv(index=False).encode("utf-8")
st.download_button(
    "Download Filtered Products (CSV)",
    data=csv,
    file_name="filtered_products.csv",
    mime="text/csv",
    use_container_width=True
)

st.caption(
    f"Dataset: {len(df):,} product records · {df['Store'].nunique()} stores · "
    f"{df['Category'].nunique()} categories · Data loaded from the attached Excel file."
)
