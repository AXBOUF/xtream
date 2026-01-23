-- ============================================================================
-- CONSOLIDATED CAR WASH MANAGEMENT SCHEMA
-- Unified schema combining wash_orders and washdata for end-to-end system
-- ============================================================================

-- ============================================================================
-- SERVICE TYPES ENUM (for data consistency)
-- ============================================================================
CREATE TYPE wash_service_type AS ENUM ('handpolish', 'xtream', 'deluxe');


-- ============================================================================
-- MAIN ORDERS TABLE (consolidated schema)
-- ============================================================================
CREATE TABLE IF NOT EXISTS wash_orders (
    id SERIAL PRIMARY KEY,
    
    -- Customer Information
    phone_number VARCHAR(20) NOT NULL,
    customer_name VARCHAR(100),
    
    -- Service Details
    wash_type wash_service_type NOT NULL DEFAULT 'xtream',
    service_duration_minutes INT,
    comments TEXT,
    
    -- Operational Tracking
    dockerid TEXT,
    operator_name VARCHAR(100),
    station_id INT,
    picked_by_hendra BOOLEAN DEFAULT FALSE,
    
    -- Vehicle Information
    vehicle_plate VARCHAR(20),
    vehicle_type VARCHAR(50),
    
    -- Timing
    entry_time TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    checkout_estimated_time TIMESTAMP WITH TIME ZONE,
    checkout_actual_time TIMESTAMP WITH TIME ZONE,
    
    -- Payment
    payment_method VARCHAR(20) DEFAULT 'cash',
    price_paid NUMERIC(8,2) NOT NULL DEFAULT 0,
    discount_applied NUMERIC(8,2) DEFAULT 0,
    notes_payment TEXT,
    
    -- Status & Audit
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'completed', 'cancelled')),
    created_date DATE NOT NULL DEFAULT CURRENT_DATE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    CONSTRAINT chk_price_nonneg CHECK (price_paid >= 0),
    CONSTRAINT chk_discount_nonneg CHECK (discount_applied >= 0)
);

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================
CREATE INDEX IF NOT EXISTS idx_wash_orders_phone ON wash_orders(phone_number);
CREATE INDEX IF NOT EXISTS idx_wash_orders_created_date ON wash_orders(created_date);
CREATE INDEX IF NOT EXISTS idx_wash_orders_entry_time ON wash_orders(entry_time);
CREATE INDEX IF NOT EXISTS idx_wash_orders_status ON wash_orders(status);
CREATE INDEX IF NOT EXISTS idx_wash_orders_payment_method ON wash_orders(payment_method);
CREATE INDEX IF NOT EXISTS idx_wash_orders_operator ON wash_orders(operator_name);
CREATE INDEX IF NOT EXISTS idx_wash_orders_dockerid ON wash_orders(dockerid);


-- ============================================================================
-- PRICE LOOKUP TABLE (for easy management of service rates)
-- ============================================================================
CREATE TABLE IF NOT EXISTS service_prices (
    service_type wash_service_type PRIMARY KEY,
    base_price NUMERIC(8,2) NOT NULL,
    description TEXT,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

INSERT INTO service_prices (service_type, base_price, description) 
VALUES 
    ('handpolish', 10.00, 'Hand Polish Service'),
    ('xtream', 15.00, 'Xtream Wash Service'),
    ('deluxe', 20.00, 'Deluxe Premium Wash')
ON CONFLICT (service_type) DO NOTHING;


-- ============================================================================
-- TRIGGER: Auto-set price based on wash_type
-- ============================================================================
CREATE OR REPLACE FUNCTION set_price_paid()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF NEW.price_paid IS NULL OR NEW.price_paid = 0 THEN
        SELECT base_price INTO NEW.price_paid
        FROM service_prices
        WHERE service_type = NEW.wash_type;
    END IF;
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trig_set_price_paid ON wash_orders;
CREATE TRIGGER trig_set_price_paid
BEFORE INSERT ON wash_orders
FOR EACH ROW
EXECUTE FUNCTION set_price_paid();


-- ============================================================================
-- TRIGGER: Update updated_at timestamp on modification
-- ============================================================================
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trig_update_updated_at ON wash_orders;
CREATE TRIGGER trig_update_updated_at
BEFORE UPDATE ON wash_orders
FOR EACH ROW
EXECUTE FUNCTION update_updated_at();


-- ============================================================================
-- SAMPLE DATA (for testing and demo)
-- ============================================================================
INSERT INTO wash_orders (phone_number, customer_name, wash_type, operator_name, dockerid, entry_time, status)
VALUES
    ('+628100000001', 'Budi', 'handpolish', 'Hendra', 'dock-01', NOW() - INTERVAL '2 hours', 'completed'),
    ('+628100000002', 'Siti', 'xtream', 'Joko', 'dock-02', NOW() - INTERVAL '1 hour', 'completed'),
    ('+628100000003', 'Ahmad', 'deluxe', 'Hendra', 'dock-03', NOW() - INTERVAL '30 minutes', 'in_progress'),
    ('+628100000004', 'Rini', 'handpolish', 'Joko', 'dock-04', NOW() - INTERVAL '15 minutes', 'in_progress'),
    ('+628100000005', 'Doni', 'xtream', 'Hendra', 'dock-05', NOW(), 'pending'),
    ('+628100000006', 'Nurul', 'deluxe', 'Joko', 'dock-06', NOW() + INTERVAL '5 minutes', 'pending'),
    ('+628100000007', 'Eka', 'xtream', 'Hendra', 'dock-07', NOW() - INTERVAL '45 minutes', 'completed'),
    ('+628100000008', 'Farah', 'handpolish', 'Joko', 'dock-08', NOW() - INTERVAL '3 hours', 'completed'),
    ('+628100000009', 'Gita', 'deluxe', 'Hendra', 'dock-09', NOW() - INTERVAL '90 minutes', 'completed')
ON CONFLICT DO NOTHING;


-- ============================================================================
-- VIEW: Daily Sales Summary (for dashboard)
-- ============================================================================
CREATE OR REPLACE VIEW vw_daily_sales_summary AS
SELECT
    created_date,
    COUNT(*) as total_orders,
    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_orders,
    COUNT(CASE WHEN status = 'in_progress' THEN 1 END) as in_progress_orders,
    SUM(price_paid) FILTER (WHERE status = 'completed') as total_revenue,
    AVG(price_paid) FILTER (WHERE status = 'completed') as avg_order_value,
    MAX(entry_time) as last_order_time
FROM wash_orders
GROUP BY created_date
ORDER BY created_date DESC;


-- ============================================================================
-- VIEW: Hourly Service Breakdown (for analytics)
-- ============================================================================
CREATE OR REPLACE VIEW vw_hourly_service_breakdown AS
SELECT
    DATE_TRUNC('hour', entry_time) as hour,
    wash_type,
    COUNT(*) as count,
    SUM(price_paid) as revenue
FROM wash_orders
WHERE status = 'completed'
GROUP BY DATE_TRUNC('hour', entry_time), wash_type
ORDER BY hour DESC, wash_type;


-- ============================================================================
-- VIEW: Top Customers (repeat customers by order count)
-- ============================================================================
CREATE OR REPLACE VIEW vw_top_customers AS
SELECT
    phone_number,
    customer_name,
    COUNT(*) as total_orders,
    SUM(price_paid) as total_spent,
    MAX(entry_time) as last_visit,
    MIN(entry_time) as first_visit
FROM wash_orders
WHERE status = 'completed'
GROUP BY phone_number, customer_name
HAVING COUNT(*) > 0
ORDER BY total_orders DESC
LIMIT 50;