# Python Analysis Notebook — Data Engineer Assignment

import pandas as pd
import numpy as np

print("\n-----------------------------")
print("NDVI Analysis (before/after sowing)")
print("-----------------------------")

cleaned = pd.read_csv("cleaned_parcel_timeseries.csv")
metadata = pd.read_csv("parcel_metadata.csv")

cleaned['date'] = pd.to_datetime(cleaned['date'], errors='coerce')
metadata['sowing_date'] = pd.to_datetime(metadata['sowing_date'], errors='coerce')


# Only keep rows with sensor_status == OK
valid = cleaned[cleaned['sensor_status'] == 'OK'].copy()

results = []

for crop, group in valid.groupby('crop_type'):
    parcels = group['parcel_id'].unique()
    ndvi_before, ndvi_after = [], []
    
    for parcel in parcels:
        sow_date = metadata.loc[metadata['parcel_id'] == parcel, 'sowing_date']
        if sow_date.empty or pd.isna(sow_date.values[0]):
            continue
        sow_date = sow_date.values[0]
        
        # Filter readings for this parcel
        parcel_data = group[group['parcel_id'] == parcel]
        
        # NDVI 30 days before sowing
        before = parcel_data[
            (parcel_data['date'] >= sow_date - pd.Timedelta(days=30)) &
            (parcel_data['date'] < sow_date)
        ]['ndvi_value']
        
        # NDVI 30 days after sowing
        after = parcel_data[
            (parcel_data['date'] > sow_date) &
            (parcel_data['date'] <= sow_date + pd.Timedelta(days=30))
        ]['ndvi_value']
        
        if not before.empty:
            ndvi_before.append(before.mean())
        if not after.empty:
            ndvi_after.append(after.mean())
    
    results.append({
        "crop_type": crop,
        "mean_ndvi_before": np.mean(ndvi_before) if ndvi_before else np.nan,
        "mean_ndvi_after": np.mean(ndvi_after) if ndvi_after else np.nan,
        "n_parcels": len(parcels)
    })

analysis_df = pd.DataFrame(results)
print(analysis_df)