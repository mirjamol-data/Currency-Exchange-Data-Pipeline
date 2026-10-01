# Currency Exchange Data Pipeline

##  Executive Summary
This project is an automated, end-to-end ETL (Extract, Transform, Load) data pipeline that fetches daily currency exchange rates from the Frankfurter API and processes them into a business-ready Microsoft SQL Server database. 

Designed with a **Medallion Architecture** (Bronze, Silver, Gold), the project demonstrates data engineering principles, including API integration, robust error handling, dimensional modeling, and the strategic delegation of transformations between Python and SQL.

## 🛠️ Technology Stack & Skills Demonstrated
*   **Languages:** Python, T-SQL
*   **Database:** Microsoft SQL Server (SSMS)
*   **Libraries:** `requests` (API extraction), `pyodbc` (database connectivity), `schedule` (orchestration), `pytest` (unit testing), `logging`, `tenacity` (retry logic)
*   **Core Concepts:** Medallion Architecture, Dimensional Modeling (Star Schema), Incremental Loading, SQL Window Functions, API Rate/Error Handling.

---

##  Pipeline Architecture & Logic

### 1. Bronze Layer (Raw Data Ingestion)
**Logic:** Acts as an immutable audit log. Python extracts data via the Frankfurter API and appends the raw JSON payload along with metadata (`fetch_date`, `inserted_at`) directly into the database.
*   **Skills Applied:** 
    *   API integration and HTTP error handling.
    *   Implementing a historical backfill script to loop through past dates and populate the database with historical data.
    *   Idempotent design: checking for existing `fetch_date` records before insertion to prevent duplicate raw entries.

### 2. Silver Layer (Data Cleaning & Validation)
**Logic:** Transforms the raw, nested JSON into a flattened relational format (`cleaned_rates`). 
*   **Skills Applied:**
    *   **Data Validation:** Python scripts unpack the JSON, cast data types, and filter out invalid rows (e.g., ensuring exchange rates are strictly `> 0`).
    *   **Graceful Error Handling:** The pipeline is configured to track specific currencies (USD to EUR, GBP, UZS, RUB). Because the source relies on European Central Bank (ECB) data, niche currencies (UZS) or suspended currencies (RUB) are often missing from the payload. Instead of failing, the Python script identifies missing keys, logs a warning via the `logging` module, and safely processes the available data.
    *   **Batch Processing:** Uses `executemany` for efficient database insertions.

### 3. Gold Layer (Business-Ready Aggregations)
**Logic:** Modeled as a Star Schema, joining the Silver fact table with dimension tables (`dim_dates`, `dim_currencies`). 
*   **Skills Applied:**
    *   **Architectural Decision:** Rather than using Python/Pandas for aggregations, the Gold layer is implemented entirely as **T-SQL Views**. This delegates the heavy lifting to the SQL Server engine, ensuring the business layer is always perfectly synced with the Silver layer without requiring additional physical storage or Python processing time.
    *   **Advanced SQL (Window Functions):** Utilized `LAG()` to calculate day-over-day percentage changes, and `AVG() OVER (ROWS BETWEEN 6 PRECEDING AND CURRENT ROW)` to generate rolling 7-day averages partitioned by currency.
    *   **Dimensional Modeling:** Pre-populated date dimensions effectively handle non-trading days (weekends/holidays), allowing the window functions to correctly bridge gaps in the data timeline.

---

##  Orchestration
The pipeline is fully automated using Python's `schedule` library. A master orchestrator script runs continuously on a server, triggering the incremental extraction and Silver transformation steps daily at 03:00 UTC (8:00 AM UTC+5), ensuring stakeholders have fresh metrics before the start of the business day.
