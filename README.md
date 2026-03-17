
# Real Estate Liquidity Intelligence System

A **machine learning–driven real estate recommendation engine** that evaluates commercial properties based on liquidity, velocity, and market positioning.  
Designed to assist **buyers and sellers** with clear, data-backed insights on asset performance.

---

## Overview

This project builds a **predictive analytics system** for commercial real estate by combining:

- Multiple **ML models (time-series inspired + tabular models)**
- **Statistical feature engineering**
- **Real-time API serving using FastAPI**
- **Cloud database integration (Supabase)**
- **LLM-generated human-readable recommendations**

The system outputs:
- Liquidity Score
- Velocity Score
- Ranking Score
- Priority Classification
- Plain-English Market Recommendation

---

## Core Features

### 1. Multi-Model Prediction Engine
- Uses 4 trained models:
  - `velocity_model.pkl`
  - `liquidity_model.pkl`
  - `ranking_model.pkl`
  - `priority_model.pkl`
- Each model captures a different dimension of real estate performance.

---

### 2. Feature Engineering
Derived features include:
- Rent per sqm (`rent_sqm`)
- Log-transformed size (`log_size_sqm`)
- Lease categorization (short vs long term)
- Occupancy encoding
- Commercial type encoding
- City-level aggregates from Supabase:
  - Median rent
  - Listing count

---

### 3. Real-Time API (FastAPI)

#### Base Endpoint
```

GET /

```
Returns API info.

#### Health Check
```

GET /health

```
Returns system status.

#### Recommendation Endpoint
```

POST /recommend

````

Accepts property details and returns:
- AI-generated market recommendation

---

### 4. Supabase Integration
- Stores incoming property data in `properties` table
- Fetches city-level statistics from `metrics` table
- Enables dynamic, context-aware predictions

---

### 5. LLM-Powered Recommendation Engine
- Uses **Groq API (LLM inference)**
- Converts raw model outputs into:
  - Simple
  - Non-technical
  - Market-friendly insights

---

## 📊 Prediction Pipeline

1. Input property data received via API  
2. Feature engineering applied:
   - Encoding  
   - Transformations  
   - Derived metrics  
3. City-level data fetched from Supabase  
4. Models generate:
   - Velocity score  
   - Liquidity score  
   - Ranking score  
   - Priority classification  
5. Results passed to LLM  
6. Final recommendation generated in plain English  

---

## Input Schema

Example request body:

```json
{
  "property_id": "P123",
  "city": "New York",
  "commercial_type": "office",
  "size_sqm": 1200,
  "annual_rent": 240000,
  "occupancy_status": "vacant",
  "lease_term_years": 3,
  "listing_date": "2026-01-01"
}
````

---

## Output

```json
{
  "recommendation": "This property shows steady market demand..."
}
```

---

## Running the Project

```bash
pip install -r requirements.txt
uvicorn main:app --reload --port 10000
```

---

## Project Structure

```
├── main.py
├── Model.py
├── velocity_model.pkl
├── liquidity_model.pkl
├── ranking_model.pkl
├── priority_model.pkl
├── .env
```

---


