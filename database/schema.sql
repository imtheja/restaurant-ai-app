-- Restaurant AI Multi-Restaurant Database Schema

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Restaurants table
CREATE TABLE restaurants (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    subdomain VARCHAR(100) UNIQUE,
    slug VARCHAR(100) UNIQUE,
    description TEXT,
    theme_config JSONB DEFAULT '{}',
    ai_personality TEXT DEFAULT 'warm, friendly, and helpful',
    ai_name VARCHAR(100) DEFAULT 'Sophie',
    welcome_message TEXT,
    logo_url VARCHAR(500),
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for fast lookups
CREATE INDEX idx_restaurants_subdomain ON restaurants(subdomain) WHERE active = true;
CREATE INDEX idx_restaurants_slug ON restaurants(slug) WHERE active = true;

-- Menu items table
CREATE TABLE menu_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    restaurant_id UUID NOT NULL REFERENCES restaurants(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    category VARCHAR(50) NOT NULL,
    ingredients JSONB DEFAULT '[]',
    allergens JSONB DEFAULT '[]',
    vegetarian BOOLEAN DEFAULT false,
    vegan BOOLEAN DEFAULT false,
    gluten_free BOOLEAN DEFAULT false,
    spice_level INTEGER DEFAULT 0 CHECK (spice_level >= 0 AND spice_level <= 5),
    prep_time VARCHAR(50),
    calories INTEGER,
    chef_notes TEXT,
    image_url VARCHAR(500),
    display_order INTEGER DEFAULT 0,
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for menu queries
CREATE INDEX idx_menu_items_restaurant ON menu_items(restaurant_id) WHERE active = true;
CREATE INDEX idx_menu_items_category ON menu_items(restaurant_id, category) WHERE active = true;

-- Conversations table for analytics
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    restaurant_id UUID NOT NULL REFERENCES restaurants(id) ON DELETE CASCADE,
    session_id VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    response TEXT NOT NULL,
    ai_service VARCHAR(50),
    response_time_ms INTEGER,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for conversation queries
CREATE INDEX idx_conversations_restaurant ON conversations(restaurant_id);
CREATE INDEX idx_conversations_session ON conversations(session_id);
CREATE INDEX idx_conversations_timestamp ON conversations(restaurant_id, timestamp);

-- Restaurant admins table
CREATE TABLE restaurant_admins (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    restaurant_id UUID NOT NULL REFERENCES restaurants(id) ON DELETE CASCADE,
    email VARCHAR(255) NOT NULL,
    name VARCHAR(255),
    role VARCHAR(50) DEFAULT 'admin',
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(restaurant_id, email)
);

-- Analytics summary table (materialized view)
CREATE TABLE analytics_daily (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    restaurant_id UUID NOT NULL REFERENCES restaurants(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    total_conversations INTEGER DEFAULT 0,
    unique_sessions INTEGER DEFAULT 0,
    avg_response_time_ms INTEGER,
    popular_items JSONB DEFAULT '[]',
    peak_hours JSONB DEFAULT '[]',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(restaurant_id, date)
);

-- Create update timestamp trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply trigger to tables
CREATE TRIGGER update_restaurants_updated_at BEFORE UPDATE ON restaurants
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_menu_items_updated_at BEFORE UPDATE ON menu_items
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to get restaurant statistics
CREATE OR REPLACE FUNCTION get_restaurant_stats(p_restaurant_id UUID, p_days INTEGER DEFAULT 30)
RETURNS TABLE (
    total_conversations BIGINT,
    unique_sessions BIGINT,
    avg_response_time_ms NUMERIC,
    busiest_hour INTEGER,
    popular_queries TEXT[]
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*)::BIGINT as total_conversations,
        COUNT(DISTINCT session_id)::BIGINT as unique_sessions,
        AVG(response_time_ms)::NUMERIC as avg_response_time_ms,
        MODE() WITHIN GROUP (ORDER BY EXTRACT(HOUR FROM timestamp))::INTEGER as busiest_hour,
        ARRAY_AGG(DISTINCT message ORDER BY COUNT(*) DESC LIMIT 10) as popular_queries
    FROM conversations
    WHERE restaurant_id = p_restaurant_id
        AND timestamp >= CURRENT_TIMESTAMP - INTERVAL '1 day' * p_days;
END;
$$ LANGUAGE plpgsql;

-- Sample data insertion
INSERT INTO restaurants (name, subdomain, slug, description, ai_name, welcome_message) VALUES
    ('Luigi''s Italian Bistro', 'luigi', 'luigi', 'Authentic Italian cuisine in the heart of the city', 'Sofia', 'Ciao! I''m Sofia, welcome to Luigi''s! What delicious Italian dish can I help you discover today?'),
    ('Sakura Sushi Bar', 'sakura', 'sakura', 'Fresh sushi and Japanese delicacies', 'Yuki', 'Konnichiwa! I''m Yuki from Sakura Sushi Bar. Ready to explore our fresh sushi selection?'),
    ('The Burger Joint', 'burgers', 'burger-joint', 'Gourmet burgers and craft beers', 'Max', 'Hey there! I''m Max from The Burger Joint. Hungry for an amazing burger?');

-- Sample menu items for Luigi's
INSERT INTO menu_items (restaurant_id, name, description, price, category, vegetarian, vegan, gluten_free) 
SELECT 
    id,
    'Margherita Pizza',
    'Fresh mozzarella, tomato sauce, and basil on our homemade crust',
    12.99,
    'main',
    true,
    false,
    false
FROM restaurants WHERE slug = 'luigi';

INSERT INTO menu_items (restaurant_id, name, description, price, category, vegetarian, vegan, gluten_free) 
SELECT 
    id,
    'Fettuccine Alfredo',
    'Homemade pasta in creamy parmesan sauce',
    15.99,
    'main',
    true,
    false,
    false
FROM restaurants WHERE slug = 'luigi';

-- Create read-only user for analytics
CREATE USER restaurant_analytics WITH PASSWORD 'analytics_password';
GRANT SELECT ON ALL TABLES IN SCHEMA public TO restaurant_analytics;

-- Create application user with appropriate permissions
CREATE USER restaurant_app WITH PASSWORD 'app_password';
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO restaurant_app;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO restaurant_app;