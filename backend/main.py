"""
FastAPI Backend for Car Wash Management System
Handles real-time data ingestion, API endpoints, and database operations
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime, date
from enum import Enum
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# CONSTANTS & CONFIG
# ============================================================================
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 5432)),
    'database': os.getenv('DB_NAME', 'washdata_db'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'postgres')
}

API_KEY = os.getenv('API_KEY', 'dev-key')
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')

# ============================================================================
# ENUMS
# ============================================================================
class WashServiceType(str, Enum):
    handpolish = "handpolish"
    xtream = "xtream"
    deluxe = "deluxe"

class PaymentMethod(str, Enum):
    cash = "cash"
    card = "card"
    transfer = "transfer"

class OrderStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"
    cancelled = "cancelled"

# ============================================================================
# PYDANTIC MODELS (Request/Response Schemas)
# ============================================================================
class WashOrderCreate(BaseModel):
    """Schema for creating a new wash order"""
    phone_number: str = Field(..., min_length=5, max_length=20, description="Customer phone number")
    customer_name: Optional[str] = Field(None, max_length=100)
    wash_type: WashServiceType = Field(default=WashServiceType.xtream)
    operator_name: Optional[str] = Field(None, max_length=100)
    vehicle_plate: Optional[str] = Field(None, max_length=20)
    payment_method: PaymentMethod = Field(default=PaymentMethod.cash)
    discount_applied: Optional[float] = Field(0, ge=0)
    comments: Optional[str] = None
    
    @validator('phone_number')
    def validate_phone(cls, v):
        # Basic phone validation (can be enhanced)
        v = v.replace(' ', '').replace('-', '')
        if not any(c.isdigit() for c in v):
            raise ValueError('Phone number must contain digits')
        return v

class WashOrderUpdate(BaseModel):
    """Schema for updating a wash order"""
    status: Optional[OrderStatus] = None
    checkout_actual_time: Optional[datetime] = None
    price_paid: Optional[float] = Field(None, ge=0)
    payment_method: Optional[PaymentMethod] = None
    comments: Optional[str] = None

class WashOrderResponse(BaseModel):
    """Schema for returning wash order data"""
    id: int
    phone_number: str
    customer_name: Optional[str]
    wash_type: str
    operator_name: Optional[str]
    status: str
    price_paid: float
    payment_method: str
    entry_time: datetime
    checkout_estimated_time: Optional[datetime]
    checkout_actual_time: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class DailySalesSummary(BaseModel):
    """Schema for daily sales data"""
    date: date
    total_orders: int
    completed_orders: int
    total_revenue: float
    avg_order_value: Optional[float]

class ServiceBreakdown(BaseModel):
    """Schema for service breakdown data"""
    wash_type: str
    count: int
    revenue: float
    percentage: float

# ============================================================================
# DATABASE FUNCTIONS
# ============================================================================
def get_db_connection():
    """Get PostgreSQL database connection"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except psycopg2.Error as e:
        logger.error(f"Database connection failed: {e}")
        raise HTTPException(status_code=500, detail="Database connection failed")

def dict_from_db(cur):
    """Convert database cursor to dictionary"""
    columns = [desc[0] for desc in cur.description]
    return {
        columns[index]: value
        for index, value in enumerate(cur.fetchone())
    }

# ============================================================================
# FastAPI Application
# ============================================================================
app = FastAPI(
    title="Car Wash Management API",
    description="API for managing car wash orders and sales data",
    version="1.0.0"
)

# ============================================================================
# CORS Middleware
# ============================================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure based on environment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# HEALTH CHECK ENDPOINT
# ============================================================================
@app.get("/health", tags=["Health"])
async def health_check():
    """Check API and database health"""
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
        conn.close()
        return {
            "status": "healthy",
            "database": "connected",
            "environment": ENVIRONMENT,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }, 503

# ============================================================================
# WASH ORDERS ENDPOINTS
# ============================================================================
@app.post("/api/orders", response_model=WashOrderResponse, tags=["Orders"])
async def create_wash_order(order: WashOrderCreate):
    """Create a new wash order (form submission)"""
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            insert_sql = """
            INSERT INTO wash_orders 
            (phone_number, customer_name, wash_type, operator_name, 
             payment_method, discount_applied, comments, status, created_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, CURRENT_DATE)
            RETURNING *;
            """
            
            cur.execute(insert_sql, (
                order.phone_number,
                order.customer_name,
                order.wash_type.value,
                order.operator_name,
                order.payment_method.value,
                order.discount_applied or 0,
                order.comments,
                OrderStatus.pending.value
            ))
            
            result = cur.fetchone()
            conn.commit()
            
            logger.info(f"Order created: {result['id']} for {order.phone_number}")
            return result
            
    except psycopg2.Error as e:
        conn.rollback()
        logger.error(f"Order creation failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to create order")
    finally:
        conn.close()

@app.get("/api/orders/{order_id}", response_model=WashOrderResponse, tags=["Orders"])
async def get_order(order_id: int):
    """Get a specific wash order by ID"""
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM wash_orders WHERE id = %s;", (order_id,))
            result = cur.fetchone()
            
            if not result:
                raise HTTPException(status_code=404, detail="Order not found")
            
            return result
    finally:
        conn.close()

@app.get("/api/orders", tags=["Orders"])
async def list_orders(
    phone: Optional[str] = None,
    status: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    limit: int = 100,
    offset: int = 0
):
    """List wash orders with optional filters"""
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            query = "SELECT * FROM wash_orders WHERE 1=1"
            params = []
            
            if phone:
                query += " AND phone_number ILIKE %s"
                params.append(f"%{phone}%")
            
            if status:
                query += " AND status = %s"
                params.append(status)
            
            if date_from:
                query += " AND created_date >= %s"
                params.append(date_from)
            
            if date_to:
                query += " AND created_date <= %s"
                params.append(date_to)
            
            query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
            params.extend([limit, offset])
            
            cur.execute(query, tuple(params))
            orders = cur.fetchall()
            
            # Get total count
            count_query = "SELECT COUNT(*) FROM wash_orders WHERE 1=1"
            count_params = []
            if phone:
                count_query += " AND phone_number ILIKE %s"
                count_params.append(f"%{phone}%")
            if status:
                count_query += " AND status = %s"
                count_params.append(status)
            if date_from:
                count_query += " AND created_date >= %s"
                count_params.append(date_from)
            if date_to:
                count_query += " AND created_date <= %s"
                count_params.append(date_to)
            
            cur.execute(count_query, tuple(count_params))
            total = cur.fetchone()[0]
            
            return {
                "total": total,
                "limit": limit,
                "offset": offset,
                "data": orders
            }
    finally:
        conn.close()

@app.patch("/api/orders/{order_id}", response_model=WashOrderResponse, tags=["Orders"])
async def update_order(order_id: int, update: WashOrderUpdate):
    """Update a wash order status/details"""
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Build dynamic update query
            updates = []
            params = []
            
            if update.status is not None:
                updates.append("status = %s")
                params.append(update.status.value)
            
            if update.checkout_actual_time is not None:
                updates.append("checkout_actual_time = %s")
                params.append(update.checkout_actual_time)
            
            if update.price_paid is not None:
                updates.append("price_paid = %s")
                params.append(update.price_paid)
            
            if update.payment_method is not None:
                updates.append("payment_method = %s")
                params.append(update.payment_method.value)
            
            if update.comments is not None:
                updates.append("comments = %s")
                params.append(update.comments)
            
            if not updates:
                raise HTTPException(status_code=400, detail="No updates provided")
            
            updates.append("updated_at = NOW()")
            query = f"UPDATE wash_orders SET {', '.join(updates)} WHERE id = %s RETURNING *;"
            params.append(order_id)
            
            cur.execute(query, tuple(params))
            result = cur.fetchone()
            
            if not result:
                raise HTTPException(status_code=404, detail="Order not found")
            
            conn.commit()
            logger.info(f"Order {order_id} updated")
            return result
            
    except psycopg2.Error as e:
        conn.rollback()
        logger.error(f"Order update failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to update order")
    finally:
        conn.close()

# ============================================================================
# DASHBOARD DATA ENDPOINTS
# ============================================================================
@app.get("/api/dashboard/daily-summary", tags=["Dashboard"])
async def get_daily_summary(date_from: Optional[date] = None, date_to: Optional[date] = None):
    """Get daily sales summary for dashboard"""
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            if date_from and date_to:
                cur.execute("""
                SELECT * FROM vw_daily_sales_summary 
                WHERE created_date BETWEEN %s AND %s
                ORDER BY created_date DESC;
                """, (date_from, date_to))
            else:
                cur.execute("SELECT * FROM vw_daily_sales_summary ORDER BY created_date DESC LIMIT 30;")
            
            results = cur.fetchall()
            return {"data": results}
    finally:
        conn.close()

@app.get("/api/dashboard/service-breakdown", tags=["Dashboard"])
async def get_service_breakdown(date_from: Optional[date] = None, date_to: Optional[date] = None):
    """Get service breakdown by type for dashboard"""
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            query = """
            SELECT 
                wash_type,
                COUNT(*) as count,
                SUM(price_paid) as revenue
            FROM wash_orders
            WHERE status = 'completed'
            """
            params = []
            
            if date_from:
                query += " AND created_date >= %s"
                params.append(date_from)
            
            if date_to:
                query += " AND created_date <= %s"
                params.append(date_to)
            
            query += " GROUP BY wash_type ORDER BY revenue DESC;"
            
            cur.execute(query, tuple(params))
            results = cur.fetchall()
            
            total_revenue = sum(r['revenue'] for r in results)
            
            for r in results:
                r['percentage'] = (r['revenue'] / total_revenue * 100) if total_revenue > 0 else 0
            
            return {"data": results}
    finally:
        conn.close()

@app.get("/api/dashboard/top-customers", tags=["Dashboard"])
async def get_top_customers(limit: int = 10):
    """Get top customers by order count"""
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
            SELECT * FROM vw_top_customers LIMIT %s;
            """, (limit,))
            
            results = cur.fetchall()
            return {"data": results}
    finally:
        conn.close()

@app.get("/api/dashboard/stats", tags=["Dashboard"])
async def get_dashboard_stats():
    """Get overall dashboard statistics"""
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
            SELECT
                COUNT(*) as total_orders,
                COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_orders,
                COUNT(CASE WHEN status = 'in_progress' THEN 1 END) as in_progress_orders,
                COUNT(DISTINCT phone_number) as unique_customers,
                SUM(price_paid) FILTER (WHERE status = 'completed') as total_revenue,
                AVG(price_paid) FILTER (WHERE status = 'completed') as avg_order_value,
                MAX(entry_time) as last_order_time
            FROM wash_orders;
            """)
            
            result = cur.fetchone()
            return result
    finally:
        conn.close()

# ============================================================================
# ERROR HANDLERS
# ============================================================================
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "timestamp": datetime.utcnow().isoformat()},
    )

# ============================================================================
# ROOT ENDPOINT
# ============================================================================
@app.get("/", tags=["Root"])
async def root():
    """API root endpoint with documentation links"""
    return {
        "message": "Car Wash Management API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "orders": "/api/orders",
            "dashboard": "/api/dashboard"
        }
    }

if __name__ == "__main__":
    import uvicorn
    host = os.getenv('BACKEND_HOST', '0.0.0.0')
    port = int(os.getenv('BACKEND_PORT', 8000))
    uvicorn.run(app, host=host, port=port)
