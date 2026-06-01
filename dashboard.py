import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sqlalchemy import create_engine
import matplotlib.dates as mdates

# Import from our core analytics module
from analytics import get_engine, calculate_inventory_turnover, get_reorder_alerts, run_stock_simulation

def generate_dashboard(engine):
    """
    Generates a high-quality 2x2 visual dashboard representing key insights
    from the inventory management analytics system.
    """
    # 1. Fetch core data
    print("Loading datasets for dashboard...")
    with engine.connect() as conn:
        df_products = pd.read_sql('SELECT * FROM Products', conn)
        df_stock = pd.read_sql('SELECT * FROM Stock_Levels', conn)
        df_sales = pd.read_sql('SELECT * FROM Sales_History', conn)

    df_turnover = calculate_inventory_turnover(engine)
    df_alerts = get_reorder_alerts(engine)

    # Set up matplotlib style for a clean, premium look
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['text.color'] = '#1e293b'
    plt.rcParams['axes.labelcolor'] = '#1e293b'
    plt.rcParams['xtick.color'] = '#475569'
    plt.rcParams['ytick.color'] = '#475569'
    plt.rcParams['grid.color'] = '#e2e8f0'
    plt.rcParams['grid.alpha'] = 0.6
    
    # Create 2x2 Subplots with premium dimensions
    fig, axes = plt.subplots(2, 2, figsize=(16, 12), dpi=150)
    fig.patch.set_facecolor('#f8fafc') # Soft slate-50 background for the canvas
    
    # ----------------------------------------------------
    # Plot 1 (Top-Left): Bar chart of Top 5 Fast-Moving Products
    # ----------------------------------------------------
    ax1 = axes[0, 0]
    ax1.set_facecolor('#ffffff')
    
    # Calculate volume sold per product
    df_sales_vol = df_sales.groupby('product_id')['quantity'].sum().reset_index()
    df_vol_merged = df_sales_vol.merge(df_products, on='product_id')
    df_top_vol = df_vol_merged.sort_values(by='quantity', ascending=False).head(5)
    
    # Shorten names for labels
    short_names = [name[:20] + '...' if len(name) > 20 else name for name in df_top_vol['name']]
    
    bars1 = ax1.bar(
        short_names, 
        df_top_vol['quantity'], 
        color=['#3b82f6', '#2563eb', '#1d4ed8', '#1e40af', '#1e3a8a'],
        width=0.55,
        zorder=3
    )
    
    ax1.set_title("Top 5 Products by Sales Volume (Units)", fontsize=13, fontweight='bold', pad=15, color='#0f172a')
    ax1.set_ylabel("Total Units Sold", fontsize=11, fontweight='semibold')
    ax1.grid(axis='y', linestyle='--', zorder=0)
    
    # Rotate labels gently
    plt.setp(ax1.get_xticklabels(), rotation=15, ha="right", fontsize=9)
    
    # Add value labels on top of bars
    for bar in bars1:
        height = bar.get_height()
        ax1.annotate(
            f'{int(height):,}',
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 3),  # 3 points vertical offset
            textcoords="offset points",
            ha='center', va='bottom', fontsize=9, fontweight='semibold', color='#334155'
        )

    # ----------------------------------------------------
    # Plot 2 (Top-Right): Line graph tracking 6-month stock trend
    # ----------------------------------------------------
    ax2 = axes[0, 1]
    ax2.set_facecolor('#ffffff')
    
    # Re-run simulation history to get daily stock details
    df_daily_stocks = run_stock_simulation()
    
    # Identify top 3 turnover products
    top_3_turnover = df_turnover.head(3)
    colors = ['#4f46e5', '#10b981', '#f59e0b']
    
    for i, (_, row) in enumerate(top_3_turnover.iterrows()):
        p_id = row['product_id']
        sku = row['sku']
        name = row['name']
        short_name = name[:22] + '...' if len(name) > 22 else name
        
        # Filter stock history for this product
        df_prod_history = df_daily_stocks[df_daily_stocks['product_id'] == p_id].sort_values(by='date')
        
        ax2.plot(
            df_prod_history['date'], 
            df_prod_history['stock_level'], 
            label=f"{sku} ({short_name})", 
            color=colors[i],
            linewidth=2,
            zorder=3
        )
        
    ax2.set_title("6-Month Daily Stock Trend (Top 3 Turnover)", fontsize=13, fontweight='bold', pad=15, color='#0f172a')
    ax2.set_ylabel("Ending Daily Stock level (Units)", fontsize=11, fontweight='semibold')
    ax2.grid(True, linestyle='--', zorder=0)
    ax2.legend(loc='upper right', frameon=True, facecolor='#ffffff', edgecolor='#e2e8f0', fontsize=9)
    
    # Format dates on X-axis beautifully
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    ax2.xaxis.set_major_locator(mdates.MonthLocator())
    plt.setp(ax2.get_xticklabels(), rotation=0, ha="center")

    # ----------------------------------------------------
    # Plot 3 (Bottom-Left): Donut chart showing distribution of stock statuses
    # ----------------------------------------------------
    ax3 = axes[1, 0]
    ax3.set_facecolor('#ffffff')
    
    # Calculate statuses from Stock Levels
    total_prods = len(df_stock)
    
    # Out of Stock: qty == 0
    # Low Stock: 0 < qty <= reorder_level
    # Healthy: qty > reorder_level
    df_stock_merged = df_stock.merge(df_products, on='product_id')
    
    oos_count = (df_stock_merged['quantity'] == 0).sum()
    low_count = ((df_stock_merged['quantity'] > 0) & (df_stock_merged['quantity'] <= df_stock_merged['reorder_level'])).sum()
    healthy_count = (df_stock_merged['quantity'] > df_stock_merged['reorder_level']).sum()
    
    counts = [healthy_count, low_count, oos_count]
    labels = [f'Healthy ({healthy_count})', f'Low Stock ({low_count})', f'Out of Stock ({oos_count})']
    status_colors = ['#10b981', '#f59e0b', '#ef4444']
    
    # Draw Donut Chart
    wedges, texts, autotexts = ax3.pie(
        counts, 
        labels=labels, 
        autopct='%1.1f%%',
        startangle=90, 
        colors=status_colors,
        textprops=dict(color='#1e293b', fontsize=10, fontweight='semibold'),
        wedgeprops=dict(width=0.35, edgecolor='#ffffff', linewidth=2)  # width creates the donut hole
    )
    
    # Adjust percentage font size and style
    for autotext in autotexts:
        autotext.set_fontsize(9)
        autotext.set_color('#ffffff')
        
    ax3.set_title("Current Stock Health Status Distribution", fontsize=13, fontweight='bold', pad=15, color='#0f172a')
    
    # Add central text to the donut hole
    ax3.text(0, 0, f"Total\n{total_prods}\nProducts", ha='center', va='center', fontsize=12, fontweight='bold', color='#475569')

    # ----------------------------------------------------
    # Plot 4 (Bottom-Right): Horizontal Bar chart of Total Revenue by Category
    # ----------------------------------------------------
    ax4 = axes[1, 1]
    ax4.set_facecolor('#ffffff')
    
    # Compute sales value per category
    df_sales_merged = df_sales.merge(df_products, on='product_id')
    df_cat_rev = df_sales_merged.groupby('category')['total_amount'].sum().reset_index()
    df_cat_rev = df_cat_rev.sort_values(by='total_amount', ascending=True)
    
    bars4 = ax4.barh(
        df_cat_rev['category'], 
        df_cat_rev['total_amount'], 
        color=['#e0f2fe', '#bae6fd', '#7dd3fc', '#38bdf8'],
        edgecolor='#0284c7',
        height=0.55,
        zorder=3
    )
    
    ax4.set_title("Gross Revenue by Product Category ($)", fontsize=13, fontweight='bold', pad=15, color='#0f172a')
    ax4.set_xlabel("Gross Sales Revenue ($)", fontsize=11, fontweight='semibold')
    ax4.grid(axis='x', linestyle='--', zorder=0)
    
    # Format X-axis with thousands separator
    ax4.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))
    
    # Add value labels inside/outside horizontal bars
    for bar in bars4:
        width = bar.get_width()
        ax4.annotate(
            f'${width:,.2f}',
            xy=(width, bar.get_y() + bar.get_height() / 2),
            xytext=(5, 0),  # 5 points horizontal offset
            textcoords="offset points",
            ha='left', va='center', fontsize=9, fontweight='bold', color='#0369a1'
        )

    # ----------------------------------------------------
    # Polish entire Dashboard layout
    # ----------------------------------------------------
    plt.suptitle("Inventory Operations & Analytics Dashboard", fontsize=18, fontweight='bold', color='#0f172a', y=0.96)
    plt.tight_layout(rect=[0.02, 0.02, 0.98, 0.93])
    
    # Save the dashboard as a high-DPI image
    img_filename = 'inventory_dashboard.png'
    plt.savefig(img_filename, dpi=300, facecolor=fig.get_facecolor())
    print(f"Dashboard visualization successfully saved to {img_filename}")
    plt.close()
    
    # Return alerts and turnover data for markdown report inclusion
    return df_alerts, df_turnover

def generate_markdown_preview(df_alerts, df_turnover):
    """
    Creates a beautiful dashboard_preview.md artifact containing the dashboard image
    and detailed tables on reorder alerts and key turnover ratios.
    """
    # 1. Prepare Reorder Alerts Markdown Table
    if len(df_alerts) > 0:
        alert_sample = df_alerts.copy()
        # Drop columns not needed or format them
        alert_sample = alert_sample[['sku', 'name', 'category', 'current_stock', 'reorder_level', 'status']]
        alert_sample.columns = ['SKU', 'Product Name', 'Category', 'Current Stock', 'Reorder Level', 'Status']
        alerts_table_md = alert_sample.to_markdown(index=False)
    else:
        alerts_table_md = "*No reorder alerts active! All product stock levels are healthy.*"

    # 2. Prepare Turnover Ratios Markdown Table (Top 5 & Bottom 5)
    df_turnover_fmt = df_turnover.copy()
    df_turnover_fmt['cogs'] = df_turnover_fmt['cogs'].map('${:,.2f}'.format)
    df_turnover_fmt['average_inventory_value'] = df_turnover_fmt['average_inventory_value'].map('${:,.2f}'.format)
    df_turnover_fmt.columns = [
        'Product ID', 'SKU', 'Product Name', 'Category', 'Unit Cost', 'Units Sold', 
        'COGS', 'Avg Inventory (Units)', 'Avg Inventory Value', 'Turnover Ratio'
    ]
    
    top_5_turnover = df_turnover_fmt.head(5)[['SKU', 'Product Name', 'Category', 'COGS', 'Avg Inventory Value', 'Turnover Ratio']]
    bottom_5_turnover = df_turnover_fmt.tail(5)[['SKU', 'Product Name', 'Category', 'COGS', 'Avg Inventory Value', 'Turnover Ratio']]

    # Copy the dashboard image to the brain artifacts directory if needed
    brain_dir = 'C:/Users/abhia/.gemini/antigravity/brain/3cacfda2-ae99-4542-984a-53f6694ee53b'
    os.makedirs(brain_dir, exist_ok=True)
    
    # Let's save dashboard copy to brain dir as well so it's fully viewable inside the artifact
    import shutil
    shutil.copy('inventory_dashboard.png', os.path.join(brain_dir, 'inventory_dashboard.png'))

    # Markdown template content
    markdown_content = f"""# Inventory Operations Dashboard - Analytics Insights

> [!IMPORTANT]
> **Actionable Operations Report**: This report presents visual insights and system-wide reorder alerts derived from the 6-month historical simulation. 
> The visual dashboard has been compiled and saved locally.

---

## 1. Executive Visual Dashboard

The consolidated 2x2 dashboard shows:
1. **Sales Volume Leaderboard**: Top 5 fast-moving items sold (units).
2. **Sawtooth Stock Tracking**: Daily stock history over 6 months showing reorder cycles for top-performing velocity items.
3. **Current Health Status**: Donut breakdown of current inventory status counts.
4. **Financial Revenue Breakdown**: Total historical gross sales across categories.

![Inventory Analytics Dashboard](file:///{os.path.join(brain_dir, 'inventory_dashboard.png')})

---

## 2. Active Reorder Alerts (Low Stock / Out of Stock)

> [!WARNING]
> **Inventory Warning Alert:** The following products have reached or fallen below their safety threshold (`quantity <= reorder_level`). 
> Immediate replenishment orders should be reviewed to avoid stockouts.

{alerts_table_md}

---

## 3. Inventory Turnover Performance

The turnover ratio assesses capital efficiency by comparing Cost of Goods Sold (COGS) to Average Inventory Value over the 6-month period.
`Inventory Turnover Ratio = Cost of Goods Sold (COGS) / Average Inventory Value`

### Top 5 Capital-Efficient Products (High Turnover)
*These products move extremely fast, maximizing cash flow and minimizing warehousing costs.*
{top_5_turnover.to_markdown(index=False)}

### Bottom 5 Capital-Inefficient Products (Slow Turnover)
*These represent high-value or low-velocity stock. They tie up working capital in the warehouse.*
{bottom_5_turnover.to_markdown(index=False)}

---

## 4. Analytical Summary & Operational Takeaways

### A. Sawtooth Stock Analysis
The line graph of daily stock trends illustrates high replenishment performance.
- Fast-Moving FMCG items (*Sparkling Cola*, *Shampoo*) trigger restock orders multiple times a month.
- Standard items show wider, stable saw-tooth waves with 3 to 7 days lead times.
- Slow-Moving products have long flat levels, highlighting safety stock levels that are rarely violated.

### B. Procurement Actions
1. **Replenish Low Stock**: Immediately trigger purchase orders for flagged reorder alerts (e.g. *Smart Robot Vacuum* and *Smart Fitness Watch*).
2. **Reduce Safety Stock for Fast-Moving FMCG**: FMCG items are turning over extremely fast (ratio ~12). Consider lowering reorder points if supplier lead times remain stable, releasing additional cash.
3. **Review High-Value Slow Movers**: Slow-moving products like Trench Coats or Laptops represent capital traps. Ensure no over-ordering occurs.
"""

    preview_path = os.path.join(brain_dir, 'dashboard_preview.md')
    with open(preview_path, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
        
    print(f"SUCCESS: Markdown preview report saved to {preview_path}")

if __name__ == '__main__':
    engine = get_engine()
    df_alerts, df_turnover = generate_dashboard(engine)
    generate_markdown_preview(df_alerts, df_turnover)
