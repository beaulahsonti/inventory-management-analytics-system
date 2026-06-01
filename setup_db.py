import os
import random
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from sqlalchemy import (
    create_engine, Column, Integer, String, Text, Numeric, DateTime, ForeignKey
)
from sqlalchemy.orm import declarative_base

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

# Create engine and setup SQLite database in the workspace
db_path = 'inventory_analytics.db'
engine = create_engine(f'sqlite:///{db_path}', future=True)
Base = declarative_base()

# Model Definitions
class Product(Base):
    __tablename__ = 'Products'
    
    product_id = Column(Integer, primary_key=True, autoincrement=True)
    sku = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    category = Column(String)
    price = Column(Numeric(10, 2), nullable=False)
    cost = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime, nullable=False)

class StockLevel(Base):
    __tablename__ = 'Stock_Levels'
    
    stock_id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('Products.product_id'), unique=True, nullable=False)
    quantity = Column(Integer, nullable=False, default=0)
    reorder_level = Column(Integer, default=10)
    last_updated = Column(DateTime, nullable=False)

class SalesHistory(Base):
    __tablename__ = 'Sales_History'
    
    sale_id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('Products.product_id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    sale_date = Column(DateTime, nullable=False)
    total_amount = Column(Numeric(10, 2), nullable=False)

# Recreate tables cleanly
Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)

# Product Metadata definition
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

# Create products data
product_list = []
sku_to_meta = {}

created_at_time = datetime(2025, 11, 20, 8, 0, 0) # 10 days before simulation starts

for category, classes in categories_meta.items():
    for m_class, items in classes.items():
        for item in items:
            price = round(random.uniform(item['price_range'][0], item['price_range'][1]), 2)
            cost = round(price * item['cost_pct'], 2)
            
            p_dict = {
                'sku': item['sku'],
                'name': item['name'],
                'description': item['desc'],
                'category': category,
                'price': price,
                'cost': cost,
                'created_at': created_at_time
            }
            product_list.append(p_dict)
            sku_to_meta[item['sku']] = {
                'movement_class': m_class,
                'price': price,
                'cost': cost
            }

# Bulk insert products using Pandas to_sql inside a single connection
df_products = pd.DataFrame(product_list)
with engine.begin() as conn:
    df_products.to_sql('Products', con=conn, if_exists='append', index=False)

# Read products back to get their auto-generated product_id
with engine.connect() as conn:
    df_products_db = pd.read_sql('SELECT * FROM Products', conn)

# Map SKU to product_id
sku_to_id = df_products_db.set_index('sku')['product_id'].to_dict()

# Setup simulation structures for each product
simulation_start_date = datetime(2025, 12, 1)
simulation_end_date = datetime(2026, 5, 31)

# Helper configs per movement class
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
        'qty_range': (1, 1), # Always sells 1
        'delay_prob': 0.08,
        'delay_range': (5, 10)
    }
}

# Track running stock, reorder levels, pending restocks, sales records
stocks = {}
reorder_levels = {}
pending_restocks = {} # p_id -> {'qty': int, 'arrival_date': date} or None
last_updated_dates = {}
prod_configs = {} # p_id -> config dictionary

for sku, meta in sku_to_meta.items():
    p_id = sku_to_id[sku]
    m_class = meta['movement_class']
    config = class_configs[m_class]
    
    prod_configs[p_id] = {
        'sku': sku,
        'price': meta['price'],
        'movement_class': m_class,
        'config': config
    }
    
    # Initialize initial stock level
    stocks[p_id] = random.randint(config['initial_stock_range'][0], config['initial_stock_range'][1])
    reorder_levels[p_id] = config['reorder_level']
    pending_restocks[p_id] = None
    last_updated_dates[p_id] = simulation_start_date - timedelta(days=1)

# Generate day-by-day dates
date_range = pd.date_range(start=simulation_start_date, end=simulation_end_date, freq='D')

sales_records = []
stockouts_count = 0

# Run simulation
for current_day in date_range:
    for p_id, p_info in prod_configs.items():
        sku = p_info['sku']
        price = p_info['price']
        m_class = p_info['movement_class']
        config = p_info['config']
        
        # 1. Process restocking deliveries
        restock = pending_restocks[p_id]
        if restock is not None and restock['arrival_date'].date() <= current_day.date():
            # Restock arrives!
            stocks[p_id] += restock['qty']
            last_updated_dates[p_id] = current_day
            pending_restocks[p_id] = None
            
        # 2. Simulate sales
        stock_available = stocks[p_id]
        if stock_available <= 0:
            # Stockout! Sales are 0
            stockouts_count += 1
            qty_sold = 0
        else:
            # Determine if a sale occurred today
            if random.random() < config['sale_probability']:
                # Sale occurs!
                if m_class == 'Slow-Moving':
                    qty_to_sell = 1
                else:
                    qty_to_sell = random.randint(config['qty_range'][0], config['qty_range'][1])
                
                # Cap sale at available stock
                qty_sold = min(qty_to_sell, stock_available)
                
                if qty_sold > 0:
                    stocks[p_id] -= qty_sold
                    last_updated_dates[p_id] = current_day
                    
                    # Generate a realistic timestamp during business hours (8:00 AM - 9:00 PM)
                    hour = random.randint(8, 20)
                    minute = random.randint(0, 59)
                    second = random.randint(0, 59)
                    sale_timestamp = datetime(
                        current_day.year, current_day.month, current_day.day,
                        hour, minute, second
                    )
                    
                    total_amount = round(qty_sold * price, 2)
                    sales_records.append({
                        'product_id': p_id,
                        'quantity': qty_sold,
                        'unit_price': price,
                        'sale_date': sale_timestamp,
                        'total_amount': total_amount
                    })
        
        # 3. Simulate restocking order if stock is below reorder level and no order is pending
        if stocks[p_id] < reorder_levels[p_id] and pending_restocks[p_id] is None:
            # Place restock order
            lead_days = random.randint(config['lead_time_range'][0], config['lead_time_range'][1])
            
            # Simulate restocking delay or failure
            if random.random() < config['delay_prob']:
                # Restocking is delayed
                extra_delay = random.randint(config['delay_range'][0], config['delay_range'][1])
                lead_days += extra_delay
            
            arrival_date = current_day + timedelta(days=lead_days)
            restock_batch = random.randint(config['restock_qty_range'][0], config['restock_qty_range'][1])
            
            pending_restocks[p_id] = {
                'qty': restock_batch,
                'arrival_date': arrival_date
            }

# Prepare sales history dataframe
df_sales = pd.DataFrame(sales_records)

# Bulk insert Sales History inside a clean begin transaction
with engine.begin() as conn:
    df_sales.to_sql('Sales_History', con=conn, if_exists='append', index=False)

# Prepare current stock levels dataframe
stock_level_records = []
for p_id in prod_configs.keys():
    stock_level_records.append({
        'product_id': p_id,
        'quantity': stocks[p_id],
        'reorder_level': reorder_levels[p_id],
        'last_updated': last_updated_dates[p_id]
    })

df_stock = pd.DataFrame(stock_level_records)

# Bulk insert Stock Levels inside a clean begin transaction
with engine.begin() as conn:
    df_stock.to_sql('Stock_Levels', con=conn, if_exists='append', index=False)

print(f"SUCCESS: Local SQLite database 'inventory_analytics.db' has been initialized and populated.")
print(f"Total Products inserted: {len(df_products)}")
print(f"Total Stock Level records: {len(df_stock)}")
print(f"Total Sales Transactions: {len(df_sales)}")
print(f"Total simulated Stockout incidents (days): {stockouts_count}")
