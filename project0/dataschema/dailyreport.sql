-- Simple table for car wash orders (PostgreSQL)

CREATE TABLE IF NOT EXISTS wash_orders (
    washid SERIAL PRIMARY KEY,
    dockerid TEXT,
    phone_number TEXT,
    wash_type TEXT NOT NULL CHECK (wash_type IN ('deluxe','xtream','handpolish')),
    entry_time TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    checkout_estimated_time TIMESTAMP WITH TIME ZONE,
    picked_by_hendra BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_wash_orders_phone ON wash_orders (phone_number);
-- add price column, ensure non-negative
ALTER TABLE wash_orders
    ADD COLUMN IF NOT EXISTS price_paid NUMERIC(8,2) NOT NULL DEFAULT 0;

ALTER TABLE wash_orders
    ADD CONSTRAINT IF NOT EXISTS chk_price_nonneg CHECK (price_paid >= 0);

-- trigger function to assign price based on wash_type when not provided
CREATE OR REPLACE FUNCTION set_price_paid()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF NEW.price_paid IS NULL OR NEW.price_paid = 0 THEN
        NEW.price_paid := CASE NEW.wash_type
            WHEN 'handpolish' THEN 10.00
            WHEN 'xtream'    THEN 15.00
            WHEN 'deluxe'    THEN 20.00
            ELSE 0.00
        END;
    END IF;
    RETURN NEW;
END;
$$;

-- ensure single trigger instance
DROP TRIGGER IF EXISTS trig_set_price_paid ON wash_orders;
CREATE TRIGGER trig_set_price_paid
BEFORE INSERT ON wash_orders
FOR EACH ROW
EXECUTE FUNCTION set_price_paid();

-- populate some dummy rows (price_paid left out so trigger sets it)
INSERT INTO wash_orders (dockerid, phone_number, wash_type)
VALUES
('dock-01', '+628100000001', 'handpolish'),
('dock-02', '+628100000002', 'xtream'),
('dock-03', '+628100000003', 'deluxe'),
('dock-04', '+628100000004', 'handpolish'),
('dock-05', '+628100000005', 'xtream'),
('dock-06', '+628100000006', 'deluxe'),
('dock-07', '+628100000007', 'xtream'),
('dock-08', '+628100000008', 'handpolish'),
('dock-09', '+628100000009', 'deluxe');

-- example inserting with an explicit override price
INSERT INTO wash_orders (dockerid, phone_number, wash_type, price_paid)
VALUES ('dock-99', '+628199999999', 'deluxe', 25.00);

-- update any existing rows that still have default 0
UPDATE wash_orders
SET price_paid = CASE wash_type
    WHEN 'handpolish' THEN 10.00
    WHEN 'xtream'    THEN 15.00
    WHEN 'deluxe'    THEN 20.00
    ELSE 0.00
END
WHERE price_paid = 0 OR price_paid IS NULL;