-- Create schema "doctech" if it doesn't exist
CREATE SCHEMA IF NOT EXISTS doctech;

-- Create table "file_type" in schema "doctech"
CREATE TABLE IF NOT EXISTS doctech.file_type (
    file_id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    filename TEXT NOT NULL,
    filetype TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- -- Create table "extracted_text" in schema "doctech"
-- CREATE TABLE IF NOT EXISTS doctech.extracted_text (
--     text_id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
--     file_id UUID NOT NULL REFERENCES doctech.file_type(file_id) ON DELETE CASCADE,
--     extraction_method TEXT NOT NULL,
--     extracted_text JSONB NOT NULL,
--     created_at TIMESTAMPTZ DEFAULT NOW()
-- );

-- Create table "shipment_info" in schema "doctech"
CREATE TABLE IF NOT EXISTS doctech.shipment_info (
    shipment_id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    file_id UUID NOT NULL REFERENCES doctech.file_type(file_id) ON DELETE CASCADE,
    text_id UUID REFERENCES doctech.extracted_text(text_id) ON DELETE SET NULL,
    header_name TEXT,
    temperature TEXT,
    quantity INTEGER CHECK (quantity >= 0),
    booking TEXT,
    carrier TEXT,
    feeder TEXT,
    vessel TEXT,
    port TEXT,
    etd TIMESTAMPTZ,
    eta TIMESTAMPTZ,
    cy_date DATE,
    return_date DATE,
    destination TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes to improve query performance
CREATE INDEX IF NOT EXISTS idx_shipment_info_file_id ON doctech.shipment_info(file_id);
CREATE INDEX IF NOT EXISTS idx_shipment_info_text_id ON doctech.shipment_info(text_id);
CREATE INDEX IF NOT EXISTS idx_file_type_filename ON doctech.file_type(filename);
-- CREATE INDEX IF NOT EXISTS idx_extracted_text_file_id ON doctech.extracted_text(file_id);
