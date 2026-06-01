import os
import random
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from sqlalchemy import create_engine

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

# Database connection helper
DB_PATH = 'inventory_analytics.db'
DATABASE_URI = f'sqlite:///{DB_PATH}'

def get_engine():
    return create_engine(DATABASE_URI)

def run_stock_simulation():
    """
    Re-runs the deterministic daily simulation using seed 42 to reconstruct
    the exact daily stock levels for all 50 products over the 6-month period.
    """
    # Reset random seeds
    np.random.seed(42)
    random.seed(42)

    categories_meta = {
        'Electronics': {
            'Fast-Moving': [
                {'name': 'USB-C Charging Cable (3ft)', 'sku': 'ELEC-USBC-01', 'price_range': (9.99, 14.99), 'cost_pct': 0.4, 'desc': 'High-speed charging cable'},
                {'name': 'Fast Wireless Charger', 'sku': 'ELEC-WRLS-02', 'price_range': (19.99, 29.99), 'cost_pct': 0.45, 'desc': '15W wireless charging pad'}
            ],
            'Standard': [
                {'name': 'Wireless Noise-Cancelling Headphones', 'sku': 'ELEC-HDPH-03', 'price_range': (89.99, 149.99), 'cost_pct': 0.55, 'desc': 'Over-ear bluetooth headphones'},
                {'name': 'Mechanical Gaming Keyboard', 'sku': 'ELEC-KEYB-04', 'price_range': (59.99, 99.99), 'cost_pct': 0.5, 'desc': 'RGB backlit gaming keyboard'},
                {'name': 'Ergonomic Wireless Mouse', 'sku': 'ELEC-MOUS-05', 'price_range': (24.99, 44.99), 'cost_pct': 0.45, 'desc': 'Multi-device wireless mouse'},
                {'name': 'Smart Fitness Watch', 'sku': 'ELEC-WTCH-06', 'price_range': (120.00, 199.99), 'cost_pct': 0.6, 'desc': 'Heart rate and sleep tracker'},
                {'name': 'Portable Bluetooth Speaker', 'sku': 'ELEC-SPKR-07', 'price_range': (39.99, 69.99), 'cost_pct': 0.5, 'desc': 'IPX7 waterproof speaker'}
            ],
            'Slow-Moving': [
                {'name': 'Premium 15-inch Laptop', 'sku': 'ELEC-LPTP-08', 'price_range': (899.99, 1499.99), 'cost_pct': 0.7, 'desc': 'Intel i7, 16GB RAM, 512GB SSD'},
                {'name': '34-inch Curved UltraWide Monitor', 'sku': 'ELEC-MNTR-09', 'price_range': (349.99, 499.99), 'cost_pct': 0.65, 'desc': '144Hz curved QHD monitor'},
                {'name': '4K Home Theater Projector', 'sku': 'ELEC-PROJ-10', 'price_range': (599.99, 899.99), 'cost_pct': 0.68, 'desc': '3000 lumens home cinema projector'}
            ]
        },
        'FMCG': {
            'Fast-Moving': [
                {'name': 'Sparkling Cola 12-Pack', 'sku': 'FMCG-COLA-01', 'price_range': (5.99, 7.99), 'cost_pct': 0.35, 'desc': 'Refreshing zero-sugar cola'},
                {'name': 'Whole Wheat Sliced Bread', 'sku': 'FMCG-BRED-02', 'price_range': (2.49, 3.49), 'cost_pct': 0.3, 'desc': 'Organic whole wheat loaf'},
                {'name': 'Organic Whole Milk 1 Gal', 'sku': 'FMCG-MILK-03', 'price_range': (3.99, 4.99), 'cost_pct': 0.4, 'desc': 'Grade A pasteurized whole milk'},
                {'name': 'Classic Salted Potato Chips', 'sku': 'FMCG-CHIP-04', 'price_range': (1.99, 3.49), 'cost_pct': 0.3, 'desc': 'Crispy salted family pack chips'},
                {'name': 'Antibacterial Hand Soap', 'sku': 'FMCG-SOAP-05', 'price_range': (2.99, 4.49), 'cost_pct': 0.35, 'desc': 'Liquid soap with aloe vera'},
                {'name': 'Fluoride Whitening Toothpaste', 'sku': 'FMCG-PAST-06', 'price_range': (3.49, 5.49), 'cost_pct': 0.3, 'desc': 'Fresh mint decay protection toothpaste'},
                {'name': 'Hydrating Daily Shampoo', 'sku': 'FMCG-SHMP-07', 'price_range': (5.99, 8.99), 'cost_pct': 0.4, 'desc': 'Sulfate-free hydrating shampoo'},
                {'name': 'Multi-Surface Disinfecting Wipes', 'sku': 'FMCG-WIPE-08', 'price_range': (4.99, 6.99), 'cost_pct': 0.35, 'desc': 'Kills 99.9% of bacteria pack of 80'},
                {'name': 'Liquid Laundry Detergent', 'sku': 'FMCG-DETG-09', 'price_range': (11.99, 15.99), 'cost_pct': 0.45, 'desc': 'Concentrated stain remover 64 loads'},
                {'name': 'Ultra Strong Paper Towels 6-Roll', 'sku': 'FMCG-PAPR-10', 'price_range': (8.99, 11.99), 'cost_pct': 0.4, 'desc': 'Absorbent double sheets paper towels'}
            ],
            'Standard': [
                {'name': 'Extra Virgin Olive Oil 500ml', 'sku': 'FMCG-OLIV-11', 'price_range': (9.99, 14.99), 'cost_pct': 0.5, 'desc': 'Cold-pressed extra virgin olive oil'},
                {'name': 'Gourmet Organic Spice Set', 'sku': 'FMCG-SPIC-12', 'price_range': (14.99, 19.99), 'cost_pct': 0.4, 'desc': 'Pack of 6 essential organic spices'},
                {'name': 'Pure Raw Wildflower Honey', 'sku': 'FMCG-HNY-13', 'price_range': (6.99, 9.99), 'cost_pct': 0.45, 'desc': '100% pure raw unpasteurized honey'},
                {'name': 'English Breakfast Tea 100 Bag', 'sku': 'FMCG-TEA-14', 'price_range': (4.99, 7.99), 'cost_pct': 0.35, 'desc': 'Rich robust black tea bags'},
                {'name': 'Whole Bean Medium Roast Coffee', 'sku': 'FMCG-COF-15', 'price_range': (12.99, 17.99), 'cost_pct': 0.5, 'desc': '100% Arabica medium roast whole bean'}
            ]
        },
        'Apparel': {
            'Fast-Moving': [
                {'name': 'Classic Cotton Crewneck T-Shirt', 'sku': 'APPR-TSHR-01', 'price_range': (14.99, 24.99), 'cost_pct': 0.3, 'desc': '100% premium combed cotton t-shirt'},
                {'name': 'Athletic Ankle Socks 6-Pack', 'sku': 'APPR-SOCK-02', 'price_range': (9.99, 15.99), 'cost_pct': 0.25, 'desc': 'Cushioned moisture-wicking socks'}
            ],
            'Standard': [
                {'name': 'Slim Fit Stretch Jeans', 'sku': 'APPR-JEAN-03', 'price_range': (39.99, 59.99), 'cost_pct': 0.35, 'desc': 'Classic 5-pocket denim jeans'},
                {'name': 'Fleece Pullover Hoodie', 'sku': 'APPR-HDPH-04', 'price_range': (29.99, 49.99), 'cost_pct': 0.35, 'desc': 'Soft brushed fleece warm hoodie'},
                {'name': 'Water-Resistant Windbreaker Jacket', 'sku': 'APPR-JCKT-05', 'price_range': (45.99, 79.99), 'cost_pct': 0.4, 'desc': 'Lightweight packable hooded jacket'},
                {'name': 'Daily Retro Sneakers', 'sku': 'APPR-SNKR-06', 'price_range': (60.00, 89.99), 'cost_pct': 0.45, 'desc': 'Unisex comfortable daily casual sneakers'},
                {'name': 'Casual Summer Sundress', 'sku': 'APPR-DRES-07', 'price_range': (34.99, 54.99), 'cost_pct': 0.3, 'desc': 'Floral print lightweight summer dress'},
                {'name': 'Activewear Drawstring Shorts', 'sku': 'APPR-SHRT-08', 'price_range': (19.99, 29.99), 'cost_pct': 0.3, 'desc': 'Quick-dry breathable training shorts'},
                {'name': 'Genuine Leather Dress Belt', 'sku': 'APPR-BELT-09', 'price_range': (19.99, 34.99), 'cost_pct': 0.35, 'desc': 'Classic brown genuine leather belt'},
                {'name': 'Adjustable Baseball Cap', 'sku': 'APPR-CAP-10', 'price_range': (12.99, 19.99), 'cost_pct': 0.3, 'desc': '100% cotton washed twill dad hat'}
            ],
            'Slow-Moving': [
                {'name': 'Tailored Wool Trench Coat', 'sku': 'APPR-COAT-11', 'price_range': (179.99, 249.99), 'cost_pct': 0.45, 'desc': 'Double-breasted wool blend winter coat'},
                {'name': 'Waterproof Insulated Winter Boots', 'sku': 'APPR-BOOT-12', 'price_range': (119.99, 159.99), 'cost_pct': 0.5, 'desc': 'Thermal lined heavy duty winter boots'},
                {'name': 'Classic Slim Fit Two-Piece Suit', 'sku': 'APPR-SUIT-13', 'price_range': (249.99, 399.99), 'cost_pct': 0.55, 'desc': 'Premium wool blend modern formal suit'}
            ]
        },
        'Home & Kitchen': {
            'Fast-Moving': [
                {'name': 'Non-Scratch Dish Sponges 6-Pack', 'sku': 'HOME-SPNG-01', 'price_range': (3.99, 5.99), 'cost_pct': 0.25, 'desc': 'Dual-sided durable cleaning sponges'},
                {'name': 'Drawstring Trash Bags 13 Gal 80ct', 'sku': 'HOME-TRSH-02', 'price_range': (12.99, 17.99), 'cost_pct': 0.3, 'desc': 'Heavy-duty tear-resistant trash bags'}
            ],
            'Standard': [
                {'name': '1000W High-Speed Countertop Blender', 'sku': 'HOME-BLND-03', 'price_range': (69.99, 99.99), 'cost_pct': 0.5, 'desc': 'Professional ice crushing smoothie maker'},
                {'name': 'Stainless Steel 2-Slice Toaster', 'sku': 'HOME-TOST-04', 'price_range': (24.99, 39.99), 'cost_pct': 0.45, 'desc': 'Extra-wide slot toaster with defrost option'},
                {'name': '12-Cup Programmable Drip Coffee Maker', 'sku': 'HOME-COFM-05', 'price_range': (39.99, 59.99), 'cost_pct': 0.45, 'desc': 'Brew strength control glass carafe coffee maker'},
                {'name': '10-Piece Nonstick Cookware Set', 'sku': 'HOME-COOK-06', 'price_range': (89.99, 139.99), 'cost_pct': 0.55, 'desc': 'Aluminum pots and pans set with lids'},
                {'name': 'Ceramic Coffee Mug 15oz', 'sku': 'HOME-MUG-07', 'price_range': (7.99, 11.99), 'cost_pct': 0.3, 'desc': 'Large microwave-safe ceramic mug'},
                {'name': 'Stainless Steel 24-Piece Flatware Set', 'sku': 'HOME-FLAT-08', 'price_range': (29.99, 49.99), 'cost_pct': 0.4, 'desc': 'Service for 6 mirror polished silverware set'},
                {'name': '10-Cup Water Filter Pitcher', 'sku': 'HOME-FILT-09', 'price_range': (19.99, 29.99), 'cost_pct': 0.35, 'desc': 'BPA-free water purification pitcher'}
            ],
            'Slow-Moving': [
                {'name': 'True HEPA Air Purifier for Large Rooms', 'sku': 'HOME-PURF-10', 'price_range': (129.99, 189.99), 'cost_pct': 0.55, 'desc': '3-stage filtration smart air purifier'},
                {'name': 'Semi-Automatic Espresso Machine', 'sku': 'HOME-ESPR-11', 'price_range': (299.99, 499.99), 'cost_pct': 0.6, 'desc': '15-bar pump espresso maker with milk frother'},
                {'name': 'Smart Robot Vacuum and Mop', 'sku': 'HOME-ROBT-12', 'price_range': (199.99, 349.99), 'cost_pct': 0.6, 'desc': 'LiDAR navigation smart robotic cleaner'}
            ]
        }
    }

    # Generate sequential product mapping
    sku_to_id = {}
    p_id_counter = 1
    sku_to_meta = {}

    for category, classes in categories_meta.items():
        for m_class, items in classes.items():
            for item in items:
                sku_to_id[item['sku']] = p_id_counter
                sku_to_meta[item['sku']] = {
                    'movement_class': m_class,
                    'price': round(random.uniform(item['price_range'][0], item['price_range'][1]), 2),
                    'cost_pct': item['cost_pct']
                }
                p_id_counter += 1

    simulation_start_date = datetime(2025, 12, 1)
    simulation_end_date = datetime(2026, 5, 31)

    class_configs = {
        'Fast-Moving': {
            'initial_stock_range': (150, 300),
            'reorder_level': 50,
            'restock_qty_range': (250, 450),
            'lead_time_range': (1, 3),
            'sale_probability': 0.95,
            'qty_range': (5, 25),
            'delay_prob': 0.05,
            'delay_range': (3, 7)
        },
        'Standard': {
            'initial_stock_range': (30, 70),
            'reorder_level': 15,
            'restock_qty_range': (50, 90),
            'lead_time_range': (3, 7),
            'sale_probability': 0.55,
            'qty_range': (1, 5),
            'delay_prob': 0.05,
            'delay_range': (3, 7)
        },
        'Slow-Moving': {
            'initial_stock_range': (5, 15),
            'reorder_level': 3,
            'restock_qty_range': (5, 12),
            'lead_time_range': (7, 14),
            'sale_probability': 0.10,
            'qty_range': (1, 1),
            'delay_prob': 0.08,
            'delay_range': (5, 10)
        }
    }

    stocks = {}
    reorder_levels = {}
    pending_restocks = {}
    prod_configs = {}

    for sku, meta in sku_to_meta.items():
        p_id = sku_to_id[sku]
        m_class = meta['movement_class']
        config = class_configs[m_class]
        
        prod_configs[p_id] = {
            'sku': sku,
            'movement_class': m_class,
            'config': config
        }
        stocks[p_id] = random.randint(config['initial_stock_range'][0], config['initial_stock_range'][1])
        reorder_levels[p_id] = config['reorder_level']
        pending_restocks[p_id] = None

    date_range = pd.date_range(start=simulation_start_date, end=simulation_end_date, freq='D')
    
    daily_stock_history = []

    for current_day in date_range:
        for p_id, p_info in prod_configs.items():
            sku = p_info['sku']
            m_class = p_info['movement_class']
            config = p_info['config']
            
            # Process restocking deliveries
            restock = pending_restocks[p_id]
            if restock is not None and restock['arrival_date'].date() <= current_day.date():
                stocks[p_id] += restock['qty']
                pending_restocks[p_id] = None
                
            # Record daily ending stock level
            daily_stock_history.append({
                'date': current_day,
                'product_id': p_id,
                'stock_level': stocks[p_id]
            })
            
            # Simulate sales
            stock_available = stocks[p_id]
            if stock_available > 0:
                if random.random() < config['sale_probability']:
                    if m_class == 'Slow-Moving':
                        qty_to_sell = 1
                    else:
                        qty_to_sell = random.randint(config['qty_range'][0], config['qty_range'][1])
                    qty_sold = min(qty_to_sell, stock_available)
                    stocks[p_id] -= qty_sold
            
            # Simulate restocking order
            if stocks[p_id] < reorder_levels[p_id] and pending_restocks[p_id] is None:
                lead_days = random.randint(config['lead_time_range'][0], config['lead_time_range'][1])
                if random.random() < config['delay_prob']:
                    lead_days += random.randint(config['delay_range'][0], config['delay_range'][1])
                
                arrival_date = current_day + timedelta(days=lead_days)
                restock_batch = random.randint(config['restock_qty_range'][0], config['restock_qty_range'][1])
                
                pending_restocks[p_id] = {
                    'qty': restock_batch,
                    'arrival_date': arrival_date
                }
                
    return pd.DataFrame(daily_stock_history)

def calculate_inventory_turnover(engine):
    """
    Calculates the Inventory Turnover Ratio for each product over the 6-month period.
    Inventory Turnover Ratio = Cost of Goods Sold (COGS) / Average Inventory
    - COGS = Total sales volume * Product unit cost.
    - Average Inventory = The average daily stock level over the 182 simulated days.
    """
    # 1. Load products and sales data from DB
    with engine.connect() as conn:
        df_products = pd.read_sql('SELECT product_id, sku, name, category, cost FROM Products', conn)
        df_sales = pd.read_sql('SELECT product_id, quantity FROM Sales_History', conn)
    
    # 2. Compute Cost of Goods Sold (COGS)
    df_sales_sum = df_sales.groupby('product_id')['quantity'].sum().reset_index()
    df_sales_sum.rename(columns={'quantity': 'total_units_sold'}, inplace=True)
    
    # Merge sales with products
    df_turnover = df_products.merge(df_sales_sum, on='product_id', how='left')
    df_turnover['total_units_sold'] = df_turnover['total_units_sold'].fillna(0).astype(int)
    df_turnover['cogs'] = round(df_turnover['total_units_sold'] * df_turnover['cost'], 2)
    
    # 3. Get exact daily stock levels via deterministic simulation
    df_daily_stocks = run_stock_simulation()
    
    # Calculate Average Inventory (mean daily stock level)
    df_avg_stock = df_daily_stocks.groupby('product_id')['stock_level'].mean().reset_index()
    df_avg_stock.rename(columns={'stock_level': 'average_inventory'}, inplace=True)
    df_avg_stock['average_inventory'] = round(df_avg_stock['average_inventory'], 2)
    
    # Merge Average Inventory
    df_turnover = df_turnover.merge(df_avg_stock, on='product_id', how='left')
    
    # 4. Calculate Turnover Ratio = COGS / Average Inventory Value
    df_turnover['average_inventory_value'] = round(df_turnover['average_inventory'] * df_turnover['cost'], 2)
    
    # Handle edge case where average inventory value might be 0 (prevent division by zero)
    df_turnover['inventory_turnover_ratio'] = np.where(
        df_turnover['average_inventory_value'] > 0,
        round(df_turnover['cogs'] / df_turnover['average_inventory_value'], 2),
        0.00
    )
    
    return df_turnover.sort_values(by='inventory_turnover_ratio', ascending=False)

def get_reorder_alerts(engine):
    """
    Identifies any products where the current stock level is at or below the reorder_level.
    Returns a DataFrame containing SKU, Product Name, Category, Current Stock, Reorder Level, and Alert Status.
    """
    query = """
    SELECT 
        p.product_id,
        p.sku,
        p.name,
        p.category,
        s.quantity AS current_stock,
        s.reorder_level
    FROM Stock_Levels s
    JOIN Products p ON s.product_id = p.product_id
    WHERE s.quantity <= s.reorder_level
    """
    with engine.connect() as conn:
        df_alerts = pd.read_sql(query, conn)
    
    # Add Alert Status (Out of Stock or Low Stock)
    df_alerts['status'] = np.where(df_alerts['current_stock'] == 0, 'OUT OF STOCK', 'LOW STOCK')
    return df_alerts.sort_values(by='current_stock')

if __name__ == '__main__':
    engine = get_engine()
    
    print("--- Calculating Core Inventory Turnover Ratios ---")
    df_turnover = calculate_inventory_turnover(engine)
    print(df_turnover[['sku', 'name', 'cogs', 'average_inventory_value', 'inventory_turnover_ratio']].head(10))
    
    print("\n--- Identifying Reorder Alerts ---")
    df_alerts = get_reorder_alerts(engine)
    print(df_alerts)
