CREATE TABLE symbols (
	symbol_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
	instrument_type_id INT NOT NULL,
	name TEXT NOT NULL,
	vendor_id INT NOT NULL,

	CONSTRAINT uq_symbols_type_name_vendor
		UNIQUE (instrument_type_id, name, vendor_id)
);

CREATE TABLE symbol_details (
	symbol_detail_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
	symbol_id BIGINT NOT NULL,
	description TEXT,
	example TEXT
);

CREATE TABLE vendors (
	vendor_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
	name TEXT NOT NULL
);