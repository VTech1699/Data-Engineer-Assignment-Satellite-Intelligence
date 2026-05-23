# Python Pipeline Notebook — Data Engineer Assignment

import pandas as pd
import numpy as np

print("-----------------------------")
print("1. Load Data")
print("-----------------------------")
readings = pd.read_csv("parcel_readings.csv")
metadata = pd.read_csv("parcel_metadata.csv")
print(f"Reading Rows: {len(readings)}, Columns: {len(readings.columns)}")
# print(f"{readings}")
print(f"Metadata Rows: {len(metadata)}, Columns: {len(metadata.columns)}")


print("\n-----------------------------")
print("2. Standardize Dates")
print("-----------------------------")
# Try multiple known formats
date_formats = ["%Y-%m-%d", "%d/%m/%Y", "%d-%b-%Y", "%d-%B-%Y"]

def parse_date(val):
    for fmt in date_formats:
        try:
            return pd.to_datetime(val, format=fmt)
        except (ValueError, TypeError):
            continue
    return pd.NaT  # fallback if none match

readings['date'] = readings['date'].apply(parse_date)
metadata['sowing_date'] = metadata['sowing_date'].apply(parse_date)

print(f"Reading Rows: {len(readings)}, Columns: {len(readings.columns)}")
# print(f"{readings}")
print(f"Metadata Rows: {len(metadata)}, Columns: {len(metadata.columns)}")


print("\n-----------------------------")
print("3. Clean Sensor Status")
print("-----------------------------")
print("BEFORE:-", readings.groupby('sensor_status', dropna=False).size().reset_index(name='count'))
print(f"Reading Rows: {len(readings)}, Columns: {len(readings.columns)}")
readings['sensor_status'] = (
    readings['sensor_status']
    .astype(str)
    .str.strip()
    .str.upper()
    .replace({
        "ERROR":"ERROR", "ERR":"ERROR",
        "NA":"NA", "NAN":"NA", "NONE":"NA",
        "":"NA"
    }))
print("AFTER:-", readings.groupby('sensor_status', dropna=False).size().reset_index(name='count'))
# readings = readings[readings['sensor_status'].isin(["OK", "ERROR", "NA"])]
print(f"Reading Rows: {len(readings)}, Columns: {len(readings.columns)}")


print("\n-----------------------------")
print("4. NDVI Outlier Removal")
print("-----------------------------")
# Example: capture dropped NDVI outliers
outliers = readings[(readings['ndvi_value'] < -1) | (readings['ndvi_value'] > 1)]
outliers.to_csv("dropped_ndvi_outliers.csv", index=False)

print(f"BEFORE:- Reading Rows: {len(readings)}, Columns: {len(readings.columns)}")
readings = readings[(readings['ndvi_value'] >= -1) & (readings['ndvi_value'] <= 1)]
print(f"AFTER:- Reading Rows: {len(readings)}, Columns: {len(readings.columns)}")

print("\n-----------------------------")
print("5. Handle Missing Values")
print("-----------------------------")
print(f"BEFORE Drop rows missing parcel_id or date \nReading Rows: {len(readings)}, Columns: {len(readings.columns)}")
# Drop rows missing parcel_id or date
readings = readings.dropna(subset=['parcel_id','date'])
print(f"AFTER Drop rows missing parcel_id or date \nReading Rows: {len(readings)}, Columns: {len(readings.columns)}")


# Impute rainfall/temperature with median
for col in ['rainfall_mm','temperature_c']:
    print(f"For {col} BEFORE:-", readings[col].isna().sum())
    median_val = readings[col].median()
    readings[col] = readings[col].fillna(median_val)
    print("AFTER:-", readings[col].isna().sum())


print("\n-----------------------------")
print("6. Deduplicate Readings")
print("-----------------------------")
print(f"BEFORE Reading Rows: {len(readings)}, Columns: {len(readings.columns)}")
# readings = readings.sort_values(['parcel_id','date'])
# readings = readings.drop_duplicates(subset=['parcel_id','date'], keep='first')

deleted_rows = readings[readings.duplicated(subset=['parcel_id','date'], keep='first')]
print("Rows that will be deleted:")
print(deleted_rows)

# Define priority: OK > ERROR > NA
status_priority = {"OK": 1, "ERROR": 2, "NA": 3}
# Map sensor_status to rank
readings['status_rank'] = readings['sensor_status'].map(status_priority)

# Sort by parcel/date and rank
readings = readings.sort_values(['parcel_id','date','status_rank'])
readings.to_csv("readings_sorted.csv", index=False)
# Drop duplicates, keeping the best-ranked row (OK if available)
readings = readings.drop_duplicates(subset=['parcel_id','date'], keep='first')

# # Keep only OK sensor_status rows
# readings_ok = readings[readings['sensor_status'] == "OK"].copy()

# # Group by parcel/date and take mean of numeric columns
# readings = (
#     readings_ok
#     .groupby(['parcel_id','date'], as_index=False)
#     .agg({
#         'ndvi_value':'mean',
#         'temperature_c':'mean',
#         'rainfall_mm':'mean',
#         'sensor_status':'first'  # always "OK" here
#     })
# )

# Remove helper column
readings = readings.drop(columns=['status_rank'])

print(f"AFTER Reading Rows: {len(readings)}, Columns: {len(readings.columns)}")


print("\n-----------------------------")
print("7. Join with Metadata")
print("-----------------------------")
cleaned = readings.merge(metadata, on='parcel_id', how='inner')
print(f"Cleaned Rows: {len(cleaned)}, Columns: {len(cleaned.columns)}")

print("\n-----------------------------")
print("8. Write Output")
print("-----------------------------")
cleaned.to_csv("cleaned_parcel_timeseries.csv", index=False)

print("✅ Cleaned dataset written to cleaned_parcel_timeseries.csv")
print(f"Rows: {len(cleaned)}, Columns: {len(cleaned.columns)}")

orphan = readings.merge(metadata, on='parcel_id', how='left', indicator=True)
orphan['orphan_flag'] = orphan['_merge'] == 'left_only'
orphan = orphan.drop(columns=['_merge'])

print(f"\nOrphan parcels flagged: {orphan['orphan_flag'].sum()}")

# Capture orphan parcels
orphans = orphan[orphan['orphan_flag']]
orphans.to_csv("orphan_parcels.csv", index=False)