# 🌱 Data-Engineer-Assignment-Satellite-Intelligence

This repository contains my solution to the Carnot Data Engineer take‑home assignment.  
The project demonstrates how to ingest messy field data (sensor readings, satellite indices, weather feeds, and farm metadata), perform a structured **data quality audit**, build a **cleaning pipeline**, run a **quick NDVI analysis**, and reflect on **production readiness**.  

Deliverables include:
- A reproducible Python script for the pipeline
- The cleaned dataset (`cleaned_parcel_timeseries.csv`)
- A detailed README (audit, pipeline, analysis, reflection)
- A Loom walkthrough video explaining key decisions

The goal is not perfection, but to show clear thinking, transparency in data handling, and readiness for scaling to production.

## 📋 Data Quality Audit

Issues identified in `parcel_readings.csv` and `parcel_metadata.csv`:

| **Issue** | **Description** | **Prevalence** | **Decision** | **Justification** |
|-----------|-----------------|----------------|--------------|-------------------|
| **Date format inconsistencies** | Dates appear in multiple formats (`2026-01-27`, `20-Jan-2026`, `16/05/2026`). | ~15% | **Repair** | Normalize to ISO `YYYY-MM-DD`. |
| **Sensor status variants** | Values include `OK`, `ok`, `Error`, `ERROR`, `NaN`, and blanks. | ~20% | **Repair** | Standardize to uppercase (`OK`, `ERROR`, `NA`) |
| **NDVI outliers** | NDVI values outside [-1, 1], e.g., `1.832`, `-1.492`. | ~3% | **Drop** | NDVI is bounded; outliers are invalid. |
| **Missing values** | Empty rainfall, temperature, or sensor_status fields. | ~10% | **Impute / Drop** | Impute rainfall/temperature with median; drop rows missing parcel_id/date. |
| **Duplicate parcel readings** | Multiple readings per parcel/date. | ~5% | **Repair** | Keep first valid `OK` reading. |
| **Metadata orphan parcels** | Readings exist for parcels not in metadata (e.g., `PARCEL_099`, `PARCEL_098`). | ~2% | **Flag / Exclude** | Exclude from join; note in audit. |
| **Whitespace anomalies** | Trailing spaces in `sensor_status` (` OK`). | ~1% | **Repair** | Strip whitespace before standardization. |

**Summary of Fixes:**  
- Dates normalized to ISO.  
- Sensor status standardized.  
- NDVI outliers dropped.  
- Rainfall/temperature imputed; critical missing values dropped.  
- Duplicates resolved.  
- Orphan parcels excluded.  
- Whitespace stripped.

---

## ⚙️ Clean Pipeline Approach

Implemented in a **Python Script**:

1. Load both CSVs.  
2. Normalize dates with multi-format parsing.  
3. Standardize sensor status.  
4. Drop NDVI outliers.  
5. Impute rainfall/temperature, drop critical missing values.  
6. Deduplicate parcel/date readings (prioritize `OK`).  
7. Left join with metadata, flag orphan parcels.  
8. Write output → `cleaned_parcel_timeseries.csv`.

Libraries used: **Pandas**, **NumPy**.  
Output: `cleaned_parcel_timeseries.csv`.

---

## 📊 NDVI Analysis

Using the cleaned dataset, NDVI values were computed for each crop type in the **30 days before** and **30 days after** sowing (excluding non-OK sensor statuses).

| **crop_type** | **mean_ndvi_before** | **mean_ndvi_after** | **n_parcels** |
|---------------|----------------------|---------------------|---------------|
| Sugarcane     | 0.176545             | 0.336198            | 19            |
| Soybean       | 0.174625             | 0.313509            | 4             |
| Wheat         | 0.174491             | 0.311366            | 2             |

**Interpretation:**  
- Sugarcane shows the strongest NDVI increase after sowing, reflecting rapid canopy development.  
- Soybean rises significantly, consistent with early vegetative growth.  
- Wheat shows a similar increase but still indicates healthy establishment.  

---

## 🏭 Production-Readiness Reflection

If scaled to run **daily** on a dataset 100× larger:

| **Aspect** | **Change / Monitoring** | **Reasoning** |
|------------|--------------------------|---------------|
| Scalability | Switch from Pandas to **Polars/Dask/Spark**. | Handles larger-than-memory datasets efficiently. |
| Validation | Add schema validation (e.g., Great Expectations). | Prevents silent breaks from new formats. |
| Storage | Use cloud storage (S3/GCS) with partitioning. | Enables incremental updates and efficient queries. |
| Monitoring | Track % rows dropped, missingness rates, and join success. | Early warning of sensor degradation or metadata drift. |
| Silent break risk | Date parsing errors. | Could misalign sowing windows without obvious failure. |

---

## ✅ Deliverables

- **Code:** Python script + quick_analysis.  
- **Output:** `cleaned_parcel_timeseries.csv`.  
- **README:** Audit, pipeline approach, analysis, reflection.  
- **Loom video:** 5–10 min walkthrough of code, decisions, and reflection. https://www.loom.com/share/d49f1f53614e43938d145b1cd929c33f

---
