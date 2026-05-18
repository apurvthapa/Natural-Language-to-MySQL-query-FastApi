# Natural Language to SQL API

An AI-powered FastAPI application that converts natural language questions into SQL queries and retrieves insights from a shipping and logistics database.

The system allows users to interact with structured databases using plain English instead of writing SQL manually.

---

# Problem Statement

Business users often need data insights but may not know SQL or database structures.

This project solves that problem by allowing users to ask questions such as:

* Top delayed routes
* Average ship capacity by country
* Most active destination ports
* Shipment status by region
* Top operators by shipment volume

The API automatically:

* understands the user query
* identifies relevant database tables
* generates SQL queries
* validates generated SQL
* executes queries safely
* returns structured JSON responses

---

# Solution Overview

The application uses an LLM-powered pipeline to transform natural language into executable SQL queries.

Workflow:

1. User sends a natural language query
2. Intent classifier identifies relevant tables
3. Schema context is dynamically selected
4. LLM generates SQL query
5. SQL validation layer checks query safety
6. Query executes using a read-only database connection
7. Structured results are returned through the API

---

# Database Design

The project uses a relational shipping and logistics database built using 3 connected tables.

## Shipments Table

Stores shipment movement and delivery activity.

Includes:

* shipment routes
* cargo type
* shipment status
* delays
* departure and arrival timestamps

Each shipment connects:

* one ship
* one source port
* one destination port

This acts as the central transactional table in the system.

---

## Ports Table

Stores geographical and regional information about ports.

Includes:

* port names
* countries
* regions

Used for:

* route analysis
* regional shipment insights
* country-level aggregation

Example ports:

* Shanghai
* Singapore
* Rotterdam
* Mumbai
* Los Angeles

---

## Ships Table

Stores vessel and operator information.

Includes:

* ship names
* vessel types
* operator companies
* ship capacity (TEU)
* origin country

Used for:

* vessel analysis
* operator performance
* fleet capacity insights

Example operators:

* Maersk
* MSC
* ONE
* COSCO Shipping

---

# Table Relationships

The tables are connected using foreign keys:

* shipments.ship_id → ships.ship_id
* shipments.source_port_id → ports.port_id
* shipments.destination_port_id → ports.port_id

The API automatically performs joins between tables whenever required to answer complex business questions.

---

# Example Questions

* Top delayed routes
* Average delay by vessel type
* Most active destination ports
* Average ship capacity by origin country
* Shipment count by region
* Top operators by shipment volume

---

# API Workflow

User Query ---> Intent Detection ---> Schema Selection ---> SQL Generation ---> Database Execution ---> JSON Response

---

# Guardrails & Security

The application includes multiple safety layers to protect the database.

Security features:

* Only SELECT queries are allowed
* SQL injection patterns are blocked
* Prompt injection attempts are filtered
* Dangerous SQL operations are rejected
* SQL comments and multiple statements are blocked
* Database access is read-only

---

# Tech Stack

* FastAPI
* Python
* MySQL
* LangChain
* OpenAI API
* SQLAlchemy
* Pandas

---

# Deployment

Backend deployed using Render.

---

# Future Improvements

* Query caching
* Query optimization
* Better intent classification
* Visualization dashboard
* SQL explanation support
* Streaming responses
