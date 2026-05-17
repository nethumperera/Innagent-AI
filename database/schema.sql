-- ════════════════════════════════════════════════════════════════
-- InnAgent AI — Supabase PostgreSQL Schema
-- Co Host Ceylon | Hotel Management Platform
-- ════════════════════════════════════════════════════════════════

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ────────────────────────────────────────────────────────────────
-- 1. HOTELS — Hotel profiles managed by Co Host Ceylon
-- ────────────────────────────────────────────────────────────────
CREATE TABLE hotels (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    address TEXT,
    city VARCHAR(100),
    district VARCHAR(100),
    province VARCHAR(100),
    country VARCHAR(50) DEFAULT 'Sri Lanka',
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    star_rating INTEGER CHECK (star_rating BETWEEN 1 AND 5),
    total_rooms INTEGER NOT NULL DEFAULT 0,
    contact_email VARCHAR(255),
    contact_phone VARCHAR(20),
    whatsapp_number VARCHAR(20),
    manager_whatsapp VARCHAR(20),
    website_url VARCHAR(500),
    booking_com_url VARCHAR(500),
    agoda_url VARCHAR(500),
    tripadvisor_url VARCHAR(500),
    check_in_time TIME DEFAULT '14:00',
    check_out_time TIME DEFAULT '11:00',
    amenities JSONB DEFAULT '[]'::jsonb,
    policies JSONB DEFAULT '{}'::jsonb,
    minimum_rate_lkr INTEGER DEFAULT 5000,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_hotels_active ON hotels(is_active);
CREATE INDEX idx_hotels_city ON hotels(city);
CREATE INDEX idx_hotels_whatsapp ON hotels(whatsapp_number);

-- ────────────────────────────────────────────────────────────────
-- 2. ROOMS — Room types per hotel with base rates
-- ────────────────────────────────────────────────────────────────
CREATE TABLE rooms (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    hotel_id UUID NOT NULL REFERENCES hotels(id) ON DELETE CASCADE,
    room_type VARCHAR(100) NOT NULL,
    description TEXT,
    base_rate_lkr INTEGER NOT NULL,
    max_rate_lkr INTEGER,
    min_rate_lkr INTEGER,
    capacity_adults INTEGER DEFAULT 2,
    capacity_children INTEGER DEFAULT 1,
    total_count INTEGER NOT NULL DEFAULT 1,
    amenities JSONB DEFAULT '[]'::jsonb,
    bed_type VARCHAR(50),
    size_sqm DECIMAL(6, 2),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_rooms_hotel ON rooms(hotel_id);
CREATE INDEX idx_rooms_hotel_active ON rooms(hotel_id, is_active);

-- ────────────────────────────────────────────────────────────────
-- 3. BOOKINGS — Reservation records
-- ────────────────────────────────────────────────────────────────
CREATE TABLE bookings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    hotel_id UUID NOT NULL REFERENCES hotels(id) ON DELETE CASCADE,
    room_id UUID REFERENCES rooms(id),
    guest_name VARCHAR(255) NOT NULL,
    guest_email VARCHAR(255),
    guest_phone VARCHAR(20),
    check_in DATE NOT NULL,
    check_out DATE NOT NULL,
    num_guests INTEGER DEFAULT 1,
    num_rooms INTEGER DEFAULT 1,
    total_amount_lkr INTEGER NOT NULL,
    booking_source VARCHAR(50) NOT NULL DEFAULT 'direct',
    ota_booking_id VARCHAR(100),
    status VARCHAR(30) DEFAULT 'confirmed'
        CHECK (status IN ('pending', 'confirmed', 'checked_in', 'checked_out', 'cancelled', 'no_show')),
    special_requests TEXT,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_bookings_hotel ON bookings(hotel_id);
CREATE INDEX idx_bookings_hotel_dates ON bookings(hotel_id, check_in, check_out);
CREATE INDEX idx_bookings_status ON bookings(hotel_id, status);
CREATE INDEX idx_bookings_created ON bookings(hotel_id, created_at);

-- ────────────────────────────────────────────────────────────────
-- 4. GUEST CONVERSATIONS — WhatsApp/email thread storage
-- ────────────────────────────────────────────────────────────────
CREATE TABLE guest_conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    hotel_id UUID NOT NULL REFERENCES hotels(id) ON DELETE CASCADE,
    guest_phone VARCHAR(20) NOT NULL,
    guest_name VARCHAR(255),
    direction VARCHAR(10) NOT NULL CHECK (direction IN ('inbound', 'outbound')),
    channel VARCHAR(20) DEFAULT 'whatsapp' CHECK (channel IN ('whatsapp', 'email', 'sms')),
    message_body TEXT NOT NULL,
    language VARCHAR(10) DEFAULT 'english' CHECK (language IN ('english', 'sinhala', 'tamil')),
    intent VARCHAR(100),
    agent_used VARCHAR(50),
    escalated BOOLEAN DEFAULT false,
    escalation_reason TEXT,
    twilio_message_sid VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_conversations_hotel ON guest_conversations(hotel_id);
CREATE INDEX idx_conversations_phone ON guest_conversations(hotel_id, guest_phone);
CREATE INDEX idx_conversations_created ON guest_conversations(hotel_id, created_at);

-- ────────────────────────────────────────────────────────────────
-- 5. PRICING RECOMMENDATIONS — PricingAgent output history
-- ────────────────────────────────────────────────────────────────
CREATE TABLE pricing_recommendations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    hotel_id UUID NOT NULL REFERENCES hotels(id) ON DELETE CASCADE,
    room_id UUID REFERENCES rooms(id),
    room_type VARCHAR(100) NOT NULL,
    current_rate_lkr INTEGER NOT NULL,
    recommended_rate_lkr INTEGER NOT NULL,
    change_percent DECIMAL(5, 2),
    multiplier_applied DECIMAL(4, 2) DEFAULT 1.0,
    demand_signal VARCHAR(10) CHECK (demand_signal IN ('low', 'medium', 'high', 'peak')),
    reasoning TEXT,
    valid_from DATE,
    valid_to DATE,
    status VARCHAR(20) DEFAULT 'pending'
        CHECK (status IN ('pending', 'approved', 'rejected', 'applied', 'expired')),
    approved_by VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_pricing_hotel ON pricing_recommendations(hotel_id);
CREATE INDEX idx_pricing_hotel_dates ON pricing_recommendations(hotel_id, valid_from, valid_to);
CREATE INDEX idx_pricing_status ON pricing_recommendations(hotel_id, status);

-- ────────────────────────────────────────────────────────────────
-- 6. REVIEWS — Scraped reviews + response drafts
-- ────────────────────────────────────────────────────────────────
CREATE TABLE reviews (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    hotel_id UUID NOT NULL REFERENCES hotels(id) ON DELETE CASCADE,
    platform VARCHAR(50) NOT NULL,
    reviewer_name VARCHAR(255),
    star_rating INTEGER CHECK (star_rating BETWEEN 1 AND 5),
    review_text TEXT NOT NULL,
    review_date DATE,
    sentiment VARCHAR(20) CHECK (sentiment IN ('positive', 'neutral', 'negative', 'mixed')),
    issues_mentioned JSONB DEFAULT '[]'::jsonb,
    response_draft TEXT,
    response_status VARCHAR(20) DEFAULT 'pending'
        CHECK (response_status IN ('pending', 'draft_ready', 'approved', 'posted', 'skipped')),
    urgency VARCHAR(10) DEFAULT 'low'
        CHECK (urgency IN ('low', 'medium', 'high', 'critical')),
    external_review_id VARCHAR(200),
    approved_by VARCHAR(255),
    posted_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_reviews_hotel ON reviews(hotel_id);
CREATE INDEX idx_reviews_hotel_status ON reviews(hotel_id, response_status);
CREATE INDEX idx_reviews_hotel_created ON reviews(hotel_id, created_at);
CREATE INDEX idx_reviews_urgency ON reviews(hotel_id, urgency);

-- ────────────────────────────────────────────────────────────────
-- 7. MAINTENANCE TICKETS — OperationsAgent task log
-- ────────────────────────────────────────────────────────────────
CREATE TABLE maintenance_tickets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    hotel_id UUID NOT NULL REFERENCES hotels(id) ON DELETE CASCADE,
    task_type VARCHAR(20) NOT NULL
        CHECK (task_type IN ('housekeeping', 'maintenance', 'inspection')),
    room VARCHAR(20),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    priority VARCHAR(10) DEFAULT 'medium'
        CHECK (priority IN ('low', 'medium', 'high', 'urgent')),
    assigned_to VARCHAR(255),
    status VARCHAR(20) DEFAULT 'pending'
        CHECK (status IN ('pending', 'in_progress', 'completed', 'overdue', 'cancelled')),
    due_by TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_tickets_hotel ON maintenance_tickets(hotel_id);
CREATE INDEX idx_tickets_hotel_status ON maintenance_tickets(hotel_id, status);
CREATE INDEX idx_tickets_hotel_priority ON maintenance_tickets(hotel_id, priority);
CREATE INDEX idx_tickets_due ON maintenance_tickets(hotel_id, due_by);

-- ────────────────────────────────────────────────────────────────
-- 8. AGENT LOGS — Full audit trail of every agent run
-- ────────────────────────────────────────────────────────────────
CREATE TABLE agent_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    hotel_id UUID REFERENCES hotels(id) ON DELETE SET NULL,
    agent_name VARCHAR(50) NOT NULL,
    task VARCHAR(500) NOT NULL,
    input_data JSONB,
    output_data JSONB,
    confidence DECIMAL(3, 2),
    escalated BOOLEAN DEFAULT false,
    escalation_reason TEXT,
    execution_time_ms INTEGER,
    tokens_used INTEGER,
    error TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_agent_logs_hotel ON agent_logs(hotel_id);
CREATE INDEX idx_agent_logs_agent ON agent_logs(agent_name);
CREATE INDEX idx_agent_logs_created ON agent_logs(hotel_id, created_at);

-- ────────────────────────────────────────────────────────────────
-- 9. DAILY METRICS — RevPAR, ADR, occupancy snapshots
-- ────────────────────────────────────────────────────────────────
CREATE TABLE daily_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    hotel_id UUID NOT NULL REFERENCES hotels(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    total_rooms INTEGER NOT NULL,
    rooms_sold INTEGER DEFAULT 0,
    occupancy_rate DECIMAL(5, 2),
    adr_lkr INTEGER,
    revpar_lkr INTEGER,
    total_revenue_lkr INTEGER DEFAULT 0,
    direct_bookings INTEGER DEFAULT 0,
    ota_bookings INTEGER DEFAULT 0,
    cancellations INTEGER DEFAULT 0,
    no_shows INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(hotel_id, date)
);

CREATE INDEX idx_metrics_hotel_date ON daily_metrics(hotel_id, date);

-- ════════════════════════════════════════════════════════════════
-- UPDATED_AT TRIGGER FUNCTION
-- ════════════════════════════════════════════════════════════════

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply trigger to all tables with updated_at
CREATE TRIGGER set_updated_at_hotels
    BEFORE UPDATE ON hotels FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER set_updated_at_rooms
    BEFORE UPDATE ON rooms FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER set_updated_at_bookings
    BEFORE UPDATE ON bookings FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER set_updated_at_pricing
    BEFORE UPDATE ON pricing_recommendations FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER set_updated_at_reviews
    BEFORE UPDATE ON reviews FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER set_updated_at_tickets
    BEFORE UPDATE ON maintenance_tickets FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER set_updated_at_metrics
    BEFORE UPDATE ON daily_metrics FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ════════════════════════════════════════════════════════════════
-- ROW LEVEL SECURITY (RLS)
-- ════════════════════════════════════════════════════════════════

-- Enable RLS on all tables
ALTER TABLE hotels ENABLE ROW LEVEL SECURITY;
ALTER TABLE rooms ENABLE ROW LEVEL SECURITY;
ALTER TABLE bookings ENABLE ROW LEVEL SECURITY;
ALTER TABLE guest_conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE pricing_recommendations ENABLE ROW LEVEL SECURITY;
ALTER TABLE reviews ENABLE ROW LEVEL SECURITY;
ALTER TABLE maintenance_tickets ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE daily_metrics ENABLE ROW LEVEL SECURITY;

-- Service role has full access (used by backend)
CREATE POLICY "Service role full access on hotels"
    ON hotels FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Service role full access on rooms"
    ON rooms FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Service role full access on bookings"
    ON bookings FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Service role full access on guest_conversations"
    ON guest_conversations FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Service role full access on pricing_recommendations"
    ON pricing_recommendations FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Service role full access on reviews"
    ON reviews FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Service role full access on maintenance_tickets"
    ON maintenance_tickets FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Service role full access on agent_logs"
    ON agent_logs FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Service role full access on daily_metrics"
    ON daily_metrics FOR ALL USING (true) WITH CHECK (true);

-- Anon key read-only access to hotels (for public pages if needed)
CREATE POLICY "Anon read hotels"
    ON hotels FOR SELECT USING (is_active = true);

-- ════════════════════════════════════════════════════════════════
-- SEED DATA — Demo hotel for Co Host Ceylon
-- ════════════════════════════════════════════════════════════════

INSERT INTO hotels (name, slug, description, address, city, district, province, star_rating, total_rooms, contact_email, contact_phone, whatsapp_number, manager_whatsapp, minimum_rate_lkr, amenities) VALUES
(
    'Kandy Heritage Villa',
    'kandy-heritage-villa',
    'A charming 12-room boutique villa overlooking the Kandy hills, blending colonial architecture with modern comfort.',
    '45 Temple Road, Peradeniya',
    'Kandy',
    'Kandy',
    'Central',
    4,
    12,
    'reservations@kandyheritagevilla.lk',
    '+94812234567',
    '+94771234567',
    '+94777654321',
    8000,
    '["WiFi", "Pool", "Restaurant", "Spa", "Airport Transfer", "Parking", "Room Service", "Laundry"]'
),
(
    'Galle Fort Boutique',
    'galle-fort-boutique',
    'An intimate 8-room boutique hotel within the historic Galle Fort walls, steps from the lighthouse.',
    '12 Church Street, Galle Fort',
    'Galle',
    'Galle',
    'Southern',
    4,
    8,
    'hello@gallefortboutique.lk',
    '+94912245678',
    '+94772345678',
    '+94778765432',
    12000,
    '["WiFi", "Rooftop Bar", "Restaurant", "Bicycle Rental", "Airport Transfer", "Concierge"]'
);

-- Rooms for Kandy Heritage Villa
INSERT INTO rooms (hotel_id, room_type, description, base_rate_lkr, max_rate_lkr, min_rate_lkr, capacity_adults, total_count, bed_type, size_sqm) VALUES
((SELECT id FROM hotels WHERE slug = 'kandy-heritage-villa'), 'Standard Double', 'Comfortable room with garden view', 12000, 22000, 8000, 2, 4, 'Double', 28.0),
((SELECT id FROM hotels WHERE slug = 'kandy-heritage-villa'), 'Deluxe King', 'Spacious room with hill view and private balcony', 18000, 35000, 12000, 2, 4, 'King', 38.0),
((SELECT id FROM hotels WHERE slug = 'kandy-heritage-villa'), 'Heritage Suite', 'Premium suite with separate living area and panoramic views', 28000, 50000, 20000, 3, 3, 'King', 55.0),
((SELECT id FROM hotels WHERE slug = 'kandy-heritage-villa'), 'Family Room', 'Two-bedroom room ideal for families', 22000, 40000, 15000, 4, 1, 'Twin+Double', 48.0);

-- Rooms for Galle Fort Boutique
INSERT INTO rooms (hotel_id, room_type, description, base_rate_lkr, max_rate_lkr, min_rate_lkr, capacity_adults, total_count, bed_type, size_sqm) VALUES
((SELECT id FROM hotels WHERE slug = 'galle-fort-boutique'), 'Colonial Room', 'Elegant room with Dutch colonial furnishings', 15000, 28000, 12000, 2, 3, 'Double', 30.0),
((SELECT id FROM hotels WHERE slug = 'galle-fort-boutique'), 'Fort View Suite', 'Suite overlooking the fort ramparts and Indian Ocean', 25000, 45000, 18000, 2, 3, 'King', 45.0),
((SELECT id FROM hotels WHERE slug = 'galle-fort-boutique'), 'Lighthouse Penthouse', 'Top-floor suite with 360° views of the fort and ocean', 38000, 65000, 28000, 2, 2, 'King', 65.0);
