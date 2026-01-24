CREATE TABLE symbols (
	symbol_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
	instrument_type_id SMALLINT NOT NULL,
	name TEXT NOT NULL,
	vendor_id SMALLINT NOT NULL,

	CONSTRAINT uq_symbols_type_name_vendor
		UNIQUE (instrument_type_id, name, vendor_id)
);

CREATE TABLE symbol_details (
	symbol_detail_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
	symbol_id INT NOT NULL,
	description TEXT,
	example TEXT,

	CONSTRAINT fk_symbol_details_symbol
		FOREIGN KEY (symbol_id)
		REFERENCES symbols (symbol_id)
		ON DELETE CASCADE
);

CREATE TABLE vendors (
	vendor_id SMALLINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
	name TEXT NOT NULL
);

CREATE TABLE instrument_types (
	instrument_type_id SMALLINT PRIMARY KEY,
	name TEXT NOT NULL
);