import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine
import datetime

# Import deterministic stock simulation from our core analytics module
from analytics import get_engine, run_stock_simulation

# ----------------------------------------------------
# 1. Page Configuration & Premium CSS Theme Override
# ----------------------------------------------------
st.set_page_config(
    page_title="Inventory Management Analytics System",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom premium CSS styling injection
st.markdown("""
<style>
    /* Import modern clean font */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
        background-color: #0f172a; /* Slate 900 canvas background */
        color: #f8fafc; /* Slate 50 body text */
    }
    
    [data-testid="stSidebar"] {
        background-color: #1e293b !important; /* Slate 800 sidebar */
        border-right: 1px solid #334155;
    }
    
    /* Header Container styling */
    .header-container {
        background: linear-gradient(135deg, #1e1b4b 0%, #0f172a 100%);
        border: 1px solid #312e81;
        border-radius: 16px;
        padding: 2.25rem;
        margin-bottom: 2rem;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3), 0 4px 6px -4px rgba(0, 0, 0, 0.3);
    }
    
    .main-title {
        font-size: 2.5rem !important;
        font-weight: 800 !important;
        background: linear-gradient(135deg, #818cf8 0%, #34d399 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0 !important;
        letter-spacing: -0.025em;
    }
    
    .subtitle {
        font-size: 1.05rem !important;
        color: #94a3b8 !important;
        margin-top: 0.5rem !important;
        margin-bottom: 0 !important;
        font-weight: 400;
    }
    
    /* Custom SaaS KPI cards */
    .kpi-card {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        height: 100%;
    }
    
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 20px -8px rgba(99, 102, 241, 0.3);
        border-color: #6366f1;
    }
    
    .kpi-title {
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #94a3b8 !important;
        margin-bottom: 0.5rem !important;
    }
    
    .kpi-value {
        font-size: 2.1rem !important;
        font-weight: 800 !important;
        color: #ffffff !important;
        line-height: 1 !important;
        margin: 0 !important;
    }
    
    .kpi-trend {
        font-size: 0.75rem !important;
        margin-top: 0.5rem !important;
        font-weight: 500;
        display: flex;
        align-items: center;
        gap: 0.25rem;
    }
    
    /* Tabs Style Overrides */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #1e293b;
        padding: 6px;
        border-radius: 10px;
        border: 1px solid #334155;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 42px;
        white-space: pre;
        background-color: transparent;
        border-radius: 6px;
        color: #94a3b8;
        font-weight: 600;
        border: none;
        padding: 0 20px;
        transition: background-color 0.2s, color 0.2s;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #334155;
        color: #ffffff;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #4f46e5 !important;
        color: #ffffff !important;
    }
    
    /* Footer section */
    .footer {
        text-align: center;
        padding: 2rem 0;
        color: #475569;
        font-size: 0.8rem;
        border-top: 1px solid #1e293b;
        margin-top: 4rem;
    }
</style>
""", unsafe_allow_html=True)


# ----------------------------------------------------
# 2. Dynamic SKU Classifier Helper
# ----------------------------------------------------
def get_movement_class(sku):
    """
    Categorizes the product SKU into movement class categories deterministically
    to support structured filters exactly matching our database simulation setups.
    """
    suffix = sku.split("-")[-1]
    num = int(suffix) if suffix.isdigit() else 0
    
    if sku.startswith("ELEC-"):
        if num in [1, 2]: return "Fast-Moving"
        elif num in [8, 9, 10]: return "Slow-Moving"
        else: return "Standard"
    elif sku.startswith("FMCG-"):
        if num <= 10: return "Fast-Moving"
        else: return "Standard"
    elif sku.startswith("APPR-"):
        if num in [1, 2]: return "Fast-Moving"
        elif num in [11, 12, 13]: return "Slow-Moving"
        else: return "Standard"
    elif sku.startswith("HOME-"):
        if num in [1, 2]: return "Fast-Moving"
        elif num in [10, 11, 12]: return "Slow-Moving"
        else: return "Standard"
    return "Standard"


# ----------------------------------------------------
# 3. Database Data Extraction & Caching
# ----------------------------------------------------
@st.cache_data(ttl=60)  # Caches loaded data for 60 seconds
def load_dashboard_datasets():
    """
    Establishes database connection and extracts full datasets for analysis.
    """
    engine = get_engine()
    with engine.connect() as conn:
        df_products = pd.read_sql('SELECT * FROM Products', conn)
        df_stock = pd.read_sql('SELECT * FROM Stock_Levels', conn)
        df_sales = pd.read_sql('SELECT * FROM Sales_History', conn)
        
    # Inject movement class programmatically for beautiful filtering
    df_products['movement_class'] = df_products['sku'].apply(get_movement_class)
    
    # Merge stock with product details for convenience
    df_inventory = df_stock.merge(df_products, on='product_id')
    df_inventory['inventory_value_cost'] = df_inventory['quantity'] * df_inventory['cost']
    df_inventory['inventory_value_retail'] = df_inventory['quantity'] * df_inventory['price']
    
    # Classify current stock health status
    # Healthy: stock > reorder_level
    # Low Stock: 0 < stock <= reorder_level
    # Out of Stock: stock == 0
    conditions = [
        df_inventory['quantity'] == 0,
        (df_inventory['quantity'] > 0) & (df_inventory['quantity'] <= df_inventory['reorder_level']),
        df_inventory['quantity'] > df_inventory['reorder_level']
    ]
    choices = ['OUT OF STOCK', 'LOW STOCK', 'HEALTHY']
    df_inventory['stock_status'] = np.select(conditions, choices, default='HEALTHY')
    
    return df_products, df_inventory, df_sales

# Pull all datasets
df_products, df_inventory, df_sales = load_dashboard_datasets()

# Deterministic daily stock levels timeline simulation (6 months)
@st.cache_data
def load_stock_simulation_history():
    """
    Triggers deterministic stock level simulation to produce line history.
    """
    df_sim = run_stock_simulation()
    # Merge names and SKUs
    df_sim_merged = df_sim.merge(df_products, on='product_id')
    return df_sim_merged

df_daily_stocks = load_stock_simulation_history()


# ----------------------------------------------------
# 4. Sidebar Interactive Filters Layout
# ----------------------------------------------------
st.sidebar.image("https://img.icons8.com/isometric/512/box.png", width=70)
st.sidebar.markdown("<h2 style='color:#ffffff; margin-top:0.25rem;'>Operations Filter</h2>", unsafe_allow_html=True)
st.sidebar.markdown(
    '<p style="color:#94a3b8; font-size:0.85rem;">Use the selections below to filter real-time metrics and visualization cards.</p>',
    unsafe_allow_html=True
)
st.sidebar.divider()

# Filter 1: Product Category Filter
all_categories = sorted(df_products['category'].unique())
selected_categories = st.sidebar.multiselect(
    "Product Categories",
    options=all_categories,
    default=all_categories,
    help="Filter by specific catalog segments."
)

# Filter 2: Velocity / Movement Class Filter
all_classes = ["Fast-Moving", "Standard", "Slow-Moving"]
selected_classes = st.sidebar.multiselect(
    "Movement Class",
    options=all_classes,
    default=all_classes,
    help="Filter by simulated product sales frequency."
)

# Filter 3: Stock Alert Status Filter
stock_statuses = ["HEALTHY", "LOW STOCK", "OUT OF STOCK"]
selected_statuses = st.sidebar.multiselect(
    "Inventory Health Status",
    options=stock_statuses,
    default=stock_statuses,
    help="Filter by safety thresholds."
)

# Filter 4: Text Search
search_query = st.sidebar.text_input("Search SKU or Name", "", placeholder="Enter keyword...")

# Action Button: Refresh
st.sidebar.divider()
if st.sidebar.button("🔄 Force Refresh Datasets"):
    st.cache_data.clear()
    st.rerun()

# Apply filters to Master Dataframes
df_inventory_filtered = df_inventory[
    (df_inventory['category'].isin(selected_categories)) &
    (df_inventory['movement_class'].isin(selected_classes)) &
    (df_inventory['stock_status'].isin(selected_statuses))
]

if search_query:
    df_inventory_filtered = df_inventory_filtered[
        df_inventory_filtered['sku'].str.contains(search_query, case=False) |
        df_inventory_filtered['name'].str.contains(search_query, case=False)
    ]

# Merge filtered products with sales for volume calculations
filtered_product_ids = df_inventory_filtered['product_id'].unique()
df_sales_filtered = df_sales[df_sales['product_id'].isin(filtered_product_ids)]


# ----------------------------------------------------
# 5. Header Component Banner
# ----------------------------------------------------
st.markdown("""
<div class="header-container">
    <h1 class="main-title">Inventory Management Analytics System</h1>
    <p class="subtitle">Interactive SaaS Operations Console • Real-Time Database Tracking &amp; Replenishment Planner</p>
</div>
""", unsafe_allow_html=True)


# ----------------------------------------------------
# 6. KPI Dashboard Row (Total, OOS, Low Stock, Value)
# ----------------------------------------------------
# Calculating KPI parameters
total_prods_count = len(df_inventory_filtered)
oos_count = (df_inventory_filtered['stock_status'] == 'OUT OF STOCK').sum()
low_stock_count = (df_inventory_filtered['stock_status'] == 'LOW STOCK').sum()
total_valuation_cost = df_inventory_filtered['inventory_value_cost'].sum()
total_valuation_retail = df_inventory_filtered['inventory_value_retail'].sum()

# Layout Columns
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.markdown(f"""
    <div class="kpi-card" style="border-top: 4px solid #818cf8;">
        <div>
            <div class="kpi-title">Total Products</div>
            <div class="kpi-value">{total_prods_count}</div>
        </div>
        <div class="kpi-trend" style="color: #818cf8;">
            <span>● Filtered catalog depth</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with kpi2:
    status_color = "#34d399" if oos_count == 0 else "#f87171"
    status_label = "Healthy status" if oos_count == 0 else "Critical action needed"
    st.markdown(f"""
    <div class="kpi-card" style="border-top: 4px solid #f87171;">
        <div>
            <div class="kpi-title">Total Stockouts</div>
            <div class="kpi-value" style="color: {status_color} !important;">{oos_count}</div>
        </div>
        <div class="kpi-trend" style="color: {status_color};">
            <span>● {status_label}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with kpi3:
    alert_color = "#34d399" if low_stock_count == 0 else "#fbbf24"
    alert_label = "Safety stock secure" if low_stock_count == 0 else "Nearing warning levels"
    st.markdown(f"""
    <div class="kpi-card" style="border-top: 4px solid #fbbf24;">
        <div>
            <div class="kpi-title">Items Needing Reorder</div>
            <div class="kpi-value" style="color: {alert_color} !important;">{low_stock_count}</div>
        </div>
        <div class="kpi-trend" style="color: {alert_color};">
            <span>● {alert_label}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with kpi4:
    st.markdown(f"""
    <div class="kpi-card" style="border-top: 4px solid #34d399;">
        <div>
            <div class="kpi-title">Total Inventory Capital</div>
            <div class="kpi-value">${total_valuation_cost:,.2f}</div>
        </div>
        <div class="kpi-trend" style="color: #64748b;">
            <span>Valued at cost (Retail: ${total_valuation_retail:,.2f})</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# ----------------------------------------------------
# 7. Navigation Tabs Layout
# ----------------------------------------------------
tab1, tab2, tab3 = st.tabs([
    "📈 Operations & Analytics", 
    "📋 Reorder Alerts & Planning", 
    "🔍 Product Catalog Explorer"
])

# ----------------------------------------------------
# Tab 1: Operations & Analytics Visualizations
# ----------------------------------------------------
with tab1:
    st.markdown("<h3 style='margin-bottom: 1rem; color: #ffffff;'>Operations Visualizations</h3>", unsafe_allow_html=True)
    
    # Row 1: Charts
    col_chart1, col_chart2 = st.columns([1, 1])
    
    with col_chart1:
        # Chart A: Top 5 Fast Moving Products (Sales Volume)
        st.markdown("<h4 style='font-size: 1.1rem; color: #94a3b8; font-weight:600;'>Top 5 Products by Sales Volume (Units)</h4>", unsafe_allow_html=True)
        
        # Calculate volume
        if not df_sales_filtered.empty:
            df_vol = df_sales_filtered.groupby('product_id')['quantity'].sum().reset_index()
            df_vol = df_vol.merge(df_products, on='product_id')
            df_top_5 = df_vol.sort_values(by='quantity', ascending=False).head(5)
            
            fig_vol = px.bar(
                df_top_5,
                x='quantity',
                y='name',
                orientation='h',
                text='quantity',
                labels={'quantity': 'Units Sold', 'name': 'Product Name'},
                color='quantity',
                color_continuous_scale=['#4f46e5', '#6366f1', '#818cf8', '#34d399'],
            )
            fig_vol.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color='#cbd5e1',
                showlegend=False,
                margin=dict(l=0, r=20, t=10, b=10),
                height=320,
                xaxis=dict(showgrid=True, gridcolor='#334155'),
                yaxis=dict(autorange="reversed"),
                coloraxis_showscale=False
            )
            fig_vol.update_traces(textposition='outside', textfont_size=10, textfont_weight='bold')
            st.plotly_chart(fig_vol, use_container_width=True)
        else:
            st.info("No sales data available for selected filters.")
            
    with col_chart2:
        # Chart B: Financial Capital Breakdown by Category
        st.markdown("<h4 style='font-size: 1.1rem; color: #94a3b8; font-weight:600;'>Gross Revenue by Product Category</h4>", unsafe_allow_html=True)
        
        if not df_sales_filtered.empty:
            # Merge with products for category details
            df_sales_merged = df_sales_filtered.merge(df_products, on='product_id')
            df_cat_revenue = df_sales_merged.groupby('category')['total_amount'].sum().reset_index()
            
            fig_pie = px.pie(
                df_cat_revenue,
                values='total_amount',
                names='category',
                hole=0.45,
                color_discrete_sequence=['#4f46e5', '#06b6d4', '#10b981', '#fbbf24']
            )
            fig_pie.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color='#cbd5e1',
                margin=dict(l=0, r=0, t=10, b=10),
                height=320,
                legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5)
            )
            fig_pie.update_traces(
                textposition='inside', 
                textinfo='percent+label',
                marker=dict(line=dict(color='#0f172a', width=2))
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No gross revenue records match selected filters.")
            
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<h4 style='font-size: 1.1rem; color: #94a3b8; font-weight:600;'>6-Month Historical Stock Trend Analysis (Sawtooth Waves)</h4>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 0.85rem; color:#64748b; margin-top:-0.5rem;'>Observe restocking cycles, safety stock violations, and procurement performance. Select specific products to isolate patterns.</p>", unsafe_allow_html=True)
    
    # Sidebar or page-level selector for timeline trend (supports multi-select dropdown!)
    # Pre-select Top 3 turnover products for user convenience
    default_trend_skus = ["ELEC-USBC-01", "FMCG-COLA-01", "HOME-SPNG-01"]
    default_trend_ids = df_products[df_products['sku'].isin(default_trend_skus)]['product_id'].tolist()
    
    # Allow user to pick from currently filtered products
    avail_products_for_trend = df_products[df_products['product_id'].isin(filtered_product_ids)].sort_values('sku')
    
    # Select box options formatting
    product_options = {row['product_id']: f"{row['sku']} - {row['name'][:30]}..." for _, row in avail_products_for_trend.iterrows()}
    
    selected_trend_ids = st.multiselect(
        "Select Products to Trace:",
        options=list(product_options.keys()),
        default=[pid for pid in default_trend_ids if pid in product_options.keys()][:3],
        format_func=lambda x: product_options[x]
    )
    
    if selected_trend_ids:
        df_trend_filtered = df_daily_stocks[df_daily_stocks['product_id'].isin(selected_trend_ids)].sort_values('date')
        
        fig_trend = px.line(
            df_trend_filtered,
            x='date',
            y='stock_level',
            color='name',
            labels={'date': 'Date', 'stock_level': 'Daily Ending Stock Level', 'name': 'Product'},
            color_discrete_sequence=['#818cf8', '#34d399', '#f59e0b', '#ec4899', '#06b6d4']
        )
        
        # Add safety thresholds using dotted lines
        for pid in selected_trend_ids:
            prod_meta = df_inventory[df_inventory['product_id'] == pid].iloc[0]
            reorder_val = prod_meta['reorder_level']
            prod_name = prod_meta['name']
            
            fig_trend.add_hline(
                y=reorder_val,
                line_dash="dot",
                line_color="#475569",
                annotation_text=f"{prod_name[:12]} Reorder Pt ({reorder_val})",
                annotation_position="bottom right"
            )
            
        fig_trend.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#cbd5e1',
            hovermode='x unified',
            height=400,
            margin=dict(l=0, r=0, t=10, b=10),
            xaxis=dict(showgrid=True, gridcolor='#1e293b'),
            yaxis=dict(showgrid=True, gridcolor='#1e293b'),
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
        )
        st.plotly_chart(fig_trend, use_container_width=True)
    else:
        st.warning("Please select at least one product to trace the sawtooth stock trend.")


# ----------------------------------------------------
# Tab 2: Reorder Alerts & Procurement Planning
# ----------------------------------------------------
with tab2:
    st.markdown("<h3 style='margin-bottom: 0.5rem; color: #ffffff;'>Active Replenishment Alerts</h3>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 0.9rem; color:#94a3b8; margin-top:-0.25rem;'>These products have current stock levels at or below safety stock. Immediate ordering is recommended to prevent stockouts.</p>", unsafe_allow_html=True)
    
    # Filter the Master Dataframe down to only items needing attention
    alerts_df = df_inventory_filtered[df_inventory_filtered['stock_status'].isin(['OUT OF STOCK', 'LOW STOCK'])].copy()
    
    if not alerts_df.empty:
        # Calculate procurement statistics
        total_alert_count = len(alerts_df)
        total_oos_alerts = (alerts_df['stock_status'] == 'OUT OF STOCK').sum()
        
        # Calculate capital needed to restore stock to (2 * reorder_level)
        # Restore Amount = (2 * reorder_level) - quantity
        alerts_df['recommended_order'] = (alerts_df['reorder_level'] * 2.5).astype(int)
        alerts_df['estimated_cost'] = alerts_df['recommended_order'] * alerts_df['cost']
        total_procurement_investment = alerts_df['estimated_cost'].sum()
        
        # Alert Stats Panel
        col_alert_stat1, col_alert_stat2, col_alert_stat3 = st.columns(3)
        with col_alert_stat1:
            st.info(f"🚨 **Products Alerted**: {total_alert_count} items below target.")
        with col_alert_stat2:
            st.error(f"❌ **Stockout Incidents**: {total_oos_alerts} items currently at zero.")
        with col_alert_stat3:
            st.warning(f"💵 **Estimated Restocking Cost**: ${total_procurement_investment:,.2f}")
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Format the table beautifully
        table_view = alerts_df[[
            'sku', 'name', 'category', 'movement_class', 
            'quantity', 'reorder_level', 'stock_status', 
            'recommended_order', 'estimated_cost'
        ]].copy()
        
        table_view.columns = [
            'SKU', 'Product Name', 'Category', 'Velocity', 
            'Current Stock', 'Reorder Point', 'Status', 
            'Rec. Order Qty', 'Estimated Order Cost'
        ]
        
        # Streamlit premium data table with interactive sorting and coloring
        st.dataframe(
            table_view,
            column_config={
                "Current Stock": st.column_config.NumberColumn(format="%d units"),
                "Reorder Point": st.column_config.NumberColumn(format="%d units"),
                "Rec. Order Qty": st.column_config.NumberColumn(format="%d units"),
                "Estimated Order Cost": st.column_config.NumberColumn(format="$%,.2f"),
                "Status": st.column_config.TextColumn(
                    help="Status of current stock level"
                )
            },
            hide_index=True,
            use_container_width=True
        )
        
        # CSV Download button for procurement department
        csv_alerts = table_view.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Procurement Purchase Recommendations (CSV)",
            data=csv_alerts,
            file_name=f"procurement_replenishment_plan_{datetime.date.today()}.csv",
            mime="text/csv"
        )
    else:
        st.success("✅ **Operations Secure**: There are no active stockout or low-stock alerts matching your filters. All inventory levels are healthy.")


# ----------------------------------------------------
# Tab 3: Dynamic Product Catalog Explorer
# ----------------------------------------------------
with tab3:
    st.markdown("<h3 style='margin-bottom: 0.5rem; color: #ffffff;'>Product Catalog Explorer</h3>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 0.9rem; color:#94a3b8;'>Explore exact inventory metrics, margin ratios, and sales details for any individual catalog item.</p>", unsafe_allow_html=True)
    
    # Dropdown to select a specific product
    active_selection_list = df_inventory.sort_values('sku')
    product_selection_options = {row['product_id']: f"[{row['sku']}] {row['name']}" for _, row in active_selection_list.iterrows()}
    
    selected_prod_id = st.selectbox(
        "Select Product to Inspect:",
        options=list(product_options.keys()),
        format_func=lambda x: product_options[x]
    )
    
    if selected_prod_id:
        prod_record = df_inventory[df_inventory['product_id'] == selected_prod_id].iloc[0]
        
        # Margin metrics
        margin = prod_record['price'] - prod_record['cost']
        margin_pct = (margin / prod_record['price']) * 100
        
        # Fetch individual sales metrics
        prod_sales = df_sales[df_sales['product_id'] == selected_prod_id]
        total_units_sold = prod_sales['quantity'].sum() if not prod_sales.empty else 0
        total_rev = prod_sales['total_amount'].sum() if not prod_sales.empty else 0.0
        transaction_count = len(prod_sales)
        
        # Render details
        col_det1, col_det2 = st.columns([1, 1.2])
        
        with col_det1:
            st.markdown(f"### Product Details: {prod_record['name']}")
            st.markdown(f"**Description**: {prod_record['description']}")
            st.markdown(f"**SKU**: `{prod_record['sku']}`")
            st.markdown(f"**Category**: {prod_record['category']}")
            st.markdown(f"**Inventory Speed Class**: {prod_record['movement_class']}")
            
            # Progress bar for stock level relative to safety reorder level
            current_qty = prod_record['quantity']
            reorder_pt = prod_record['reorder_level']
            max_gauge = max(current_qty, reorder_pt * 3, 10)
            progress_ratio = min(float(current_qty) / float(max_gauge), 1.0)
            
            st.markdown("<br>**Current Stock Level Status:**", unsafe_allow_html=True)
            status_badge_color = "#10b981" if prod_record['stock_status'] == 'HEALTHY' else ("#f59e0b" if prod_record['stock_status'] == 'LOW STOCK' else "#ef4444")
            st.markdown(f"<span style='background-color:{status_badge_color}; color:#ffffff; padding:0.2rem 0.6rem; border-radius:6px; font-weight:bold; font-size:0.85rem;'>{prod_record['stock_status']}</span>", unsafe_allow_html=True)
            
            st.progress(progress_ratio)
            st.caption(f"Currently in Stock: **{current_qty} units** • Reorder Threshold: **{reorder_pt} units**")
            
        with col_det2:
            st.markdown("### Financials & Performance Summary")
            
            fin_col1, fin_col2 = st.columns(2)
            with fin_col1:
                st.metric("Wholesale Cost", f"${prod_record['cost']:.2f}")
                st.metric("Gross Profit Margin", f"${margin:.2f}", f"{margin_pct:.1f}%")
            with fin_col2:
                st.metric("Retail Listing Price", f"${prod_record['price']:.2f}")
                st.metric("Inventory Value (Cost)", f"${prod_record['inventory_value_cost']:.2f}")
                
            st.divider()
            
            st.markdown("### Historical Sales Performance (6 Months)")
            perf_col1, perf_col2, perf_col3 = st.columns(3)
            
            with perf_col1:
                st.metric("Units Sold", f"{total_units_sold} units")
            with perf_col2:
                st.metric("Total Revenue", f"${total_rev:,.2f}")
            with perf_col3:
                st.metric("Transactions", f"{transaction_count} sales")


# ----------------------------------------------------
# 8. Footer Section
# ----------------------------------------------------
st.markdown("""
<div class="footer">
    Inventory Management Analytics System • Powered by Streamlit, Plotly &amp; SQLite • 2026 Simulation Database Console
</div>
""", unsafe_allow_html=True)
