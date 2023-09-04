CREATE TABLE income_invoices (
    id SERIAL PRIMARY KEY,
    invoice_number VARCHAR(255) NOT NULL,
    invoice_date DATE NOT NULL,
    customer_name VARCHAR(255) NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL
);

CREATE TABLE expense_invoices (
    id SERIAL PRIMARY KEY,
    invoice_number VARCHAR(255) NOT NULL,
    invoice_date DATE NOT NULL,
    vendor_name VARCHAR(255) NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL
);
