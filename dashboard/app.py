"""
Interactive Live Sales Dashboard for Car Wash Management System
Built with Streamlit for real-time analytics and visualization
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
API_URL = os.getenv('BACKEND_URL', 'http://localhost:8000/api')
REFRESH_INTERVAL = 10  # seconds

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================
st.set_page_config(
    page_title="Xtream Wash - Live Dashboard",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    [data-testid="stMetricValue"] {
        font-size: 28px;
    }
    .stMetric {
        background-color: #f0f4ff;
        padding: 15px;
        border-radius: 10px;
        border-left: 4px solid #667eea;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================
@st.cache_data(ttl=10)
def fetch_dashboard_stats():
    """Fetch dashboard statistics from API"""
    try:
        response = requests.get(f"{API_URL}/dashboard/stats", timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error fetching stats: {e}")
        return None

@st.cache_data(ttl=10)
def fetch_daily_summary(days=30):
    """Fetch daily sales summary from API"""
    try:
        date_to = datetime.now().date()
        date_from = date_to - timedelta(days=days)
        response = requests.get(
            f"{API_URL}/dashboard/daily-summary",
            params={"date_from": date_from, "date_to": date_to},
            timeout=5
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error fetching daily summary: {e}")
        return {"data": []}

@st.cache_data(ttl=10)
def fetch_service_breakdown(days=30):
    """Fetch service breakdown from API"""
    try:
        date_to = datetime.now().date()
        date_from = date_to - timedelta(days=days)
        response = requests.get(
            f"{API_URL}/dashboard/service-breakdown",
            params={"date_from": date_from, "date_to": date_to},
            timeout=5
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error fetching service breakdown: {e}")
        return {"data": []}

@st.cache_data(ttl=10)
def fetch_top_customers(limit=10):
    """Fetch top customers from API"""
    try:
        response = requests.get(
            f"{API_URL}/dashboard/top-customers",
            params={"limit": limit},
            timeout=5
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error fetching top customers: {e}")
        return {"data": []}

# ============================================================================
# HEADER & TITLE
# ============================================================================
col1, col2 = st.columns([1, 3])
with col1:
    st.markdown("# 🚗 Xtream Wash")
with col2:
    st.markdown("### Live Sales Dashboard")

st.markdown("---")

# ============================================================================
# REFRESH CONTROL & SIDEBAR
# ============================================================================
with st.sidebar:
    st.markdown("### Dashboard Controls")
    
    # Refresh button
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    
    # Date range selector
    st.markdown("### Date Range")
    days_filter = st.slider("Days to display:", 1, 90, 30, key="days_filter")
    
    # Auto-refresh toggle
    auto_refresh = st.checkbox("Auto-refresh every 10s", value=False)
    if auto_refresh:
        st.info("Dashboard will refresh every 10 seconds")
    
    st.markdown("---")
    
    # API Status
    st.markdown("### System Status")
    try:
        health = requests.get(f"{API_URL.replace('/api', '')}/health", timeout=2).json()
        if health.get('status') == 'healthy':
            st.success("✓ API Connected")
        else:
            st.warning("⚠ API Issues")
    except:
        st.error("✗ API Disconnected")
    
    st.markdown("---")
    st.markdown("Last updated: " + datetime.now().strftime("%H:%M:%S"))

# ============================================================================
# KEY METRICS (TOP SECTION)
# ============================================================================
st.markdown("## 📊 Key Metrics")

stats = fetch_dashboard_stats()

if stats:
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            label="Total Orders",
            value=stats.get('total_orders', 0),
            delta=f"{stats.get('completed_orders', 0)} completed"
        )
    
    with col2:
        st.metric(
            label="Total Revenue",
            value=f"${stats.get('total_revenue', 0):.2f}",
            delta=f"Avg: ${stats.get('avg_order_value', 0):.2f}"
        )
    
    with col3:
        st.metric(
            label="In Progress",
            value=stats.get('in_progress_orders', 0),
            delta="Orders"
        )
    
    with col4:
        st.metric(
            label="Unique Customers",
            value=stats.get('unique_customers', 0),
            delta="Total"
        )
    
    with col5:
        last_order = stats.get('last_order_time', 'N/A')
        st.metric(
            label="Last Order",
            value=datetime.fromisoformat(last_order).strftime("%H:%M") if last_order != 'N/A' else 'N/A'
        )

st.markdown("---")

# ============================================================================
# CHARTS & VISUALIZATIONS
# ============================================================================

# Row 1: Daily Revenue & Service Breakdown
col1, col2 = st.columns(2)

# Daily Revenue Chart
with col1:
    st.markdown("#### 📈 Daily Revenue Trend")
    daily_data = fetch_daily_summary(days_filter)
    
    if daily_data['data']:
        df_daily = pd.DataFrame(daily_data['data'])
        
        if 'date' in df_daily.columns or 'created_date' in df_daily.columns:
            date_col = 'date' if 'date' in df_daily.columns else 'created_date'
            df_daily['date'] = pd.to_datetime(df_daily[date_col])
            df_daily = df_daily.sort_values('date')
            
            fig_revenue = px.line(
                df_daily,
                x='date',
                y='total_revenue',
                markers=True,
                title="",
                labels={'date': 'Date', 'total_revenue': 'Revenue ($)'}
            )
            fig_revenue.update_layout(
                hovermode='x unified',
                height=400,
                showlegend=False
            )
            st.plotly_chart(fig_revenue, use_container_width=True)
    else:
        st.info("No daily data available")

# Service Breakdown Pie Chart
with col2:
    st.markdown("#### 🎯 Service Type Distribution")
    service_data = fetch_service_breakdown(days_filter)
    
    if service_data['data']:
        df_service = pd.DataFrame(service_data['data'])
        
        fig_service = px.pie(
            df_service,
            values='revenue',
            names='wash_type',
            hover_data={'count': True, 'percentage': ':.1f'},
            title=""
        )
        fig_service.update_traces(
            textposition='inside',
            textinfo='label+percent'
        )
        fig_service.update_layout(height=400)
        st.plotly_chart(fig_service, use_container_width=True)
    else:
        st.info("No service data available")

st.markdown("---")

# Row 2: Detailed Tables
col1, col2 = st.columns(2)

# Daily Summary Table
with col1:
    st.markdown("#### 📅 Daily Summary")
    daily_data = fetch_daily_summary(days_filter)
    
    if daily_data['data']:
        df_daily_table = pd.DataFrame(daily_data['data'])
        
        # Format columns
        if 'date' not in df_daily_table.columns and 'created_date' in df_daily_table.columns:
            df_daily_table = df_daily_table.rename(columns={'created_date': 'date'})
        
        display_cols = ['date', 'total_orders', 'completed_orders', 'total_revenue', 'avg_order_value']
        df_display = df_daily_table[[col for col in display_cols if col in df_daily_table.columns]]
        
        # Format currency columns
        if 'total_revenue' in df_display.columns:
            df_display['total_revenue'] = df_display['total_revenue'].apply(lambda x: f"${x:.2f}")
        if 'avg_order_value' in df_display.columns:
            df_display['avg_order_value'] = df_display['avg_order_value'].apply(lambda x: f"${x:.2f}" if pd.notna(x) else "N/A")
        
        st.dataframe(df_display, use_container_width=True, hide_index=True)
    else:
        st.info("No data available")

# Top Customers Table
with col2:
    st.markdown("#### ⭐ Top Customers")
    customers_data = fetch_top_customers(10)
    
    if customers_data['data']:
        df_customers = pd.DataFrame(customers_data['data'])
        
        display_cols = ['phone_number', 'customer_name', 'total_orders', 'total_spent']
        df_cust_display = df_customers[[col for col in display_cols if col in df_customers.columns]]
        
        # Rename for display
        df_cust_display = df_cust_display.rename(columns={
            'phone_number': 'Phone',
            'customer_name': 'Name',
            'total_orders': 'Orders',
            'total_spent': 'Spent'
        })
        
        # Format currency
        if 'Spent' in df_cust_display.columns:
            df_cust_display['Spent'] = df_cust_display['Spent'].apply(lambda x: f"${x:.2f}")
        
        st.dataframe(df_cust_display, use_container_width=True, hide_index=True)
    else:
        st.info("No customer data available")

st.markdown("---")

# ============================================================================
# SERVICE BREAKDOWN TABLE
# ============================================================================
st.markdown("#### 🏪 Service Type Performance")
service_data = fetch_service_breakdown(days_filter)

if service_data['data']:
    df_service_table = pd.DataFrame(service_data['data'])
    
    # Format for display
    df_service_display = df_service_table.copy()
    df_service_display['revenue'] = df_service_display['revenue'].apply(lambda x: f"${x:.2f}")
    df_service_display['percentage'] = df_service_display['percentage'].apply(lambda x: f"{x:.1f}%")
    
    df_service_display = df_service_display.rename(columns={
        'wash_type': 'Service Type',
        'count': 'Orders',
        'revenue': 'Revenue',
        'percentage': 'Share'
    })
    
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.dataframe(df_service_display, use_container_width=True, hide_index=True)
else:
    st.info("No service performance data available")

st.markdown("---")

# ============================================================================
# FOOTER & INFO
# ============================================================================
st.markdown("""
<div style='text-align: center; color: #666; font-size: 12px; margin-top: 20px;'>
    <p>🚗 Xtream Wash Management System | Real-time Dashboard</p>
    <p>Data refreshes automatically • Last update: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</p>
</div>
""", unsafe_allow_html=True)

# Auto-refresh
if auto_refresh:
    import time
    time.sleep(REFRESH_INTERVAL)
    st.rerun()
