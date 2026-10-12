# Weeks 2-3, Enrich Sold and Listing data with FRED 30-year mortgage rates

import pandas as pd
import os

OUTPUT_DIR = r"C:\Users\abdif\IDX_Data\output"

# Fetch FRED MORTGAGE30US (weekly 30-year fixed mortgage rate, %)
FRED_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=MORTGAGE30US"
rates = pd.read_csv(FRED_URL, parse_dates=["observation_date"])

print(rates.head())
print(rates.tail())
print(f"Weekly rate rows: {len(rates):,}")


# Resample weekly rates to monthly averages
rates = rates.set_index("observation_date")
monthly_rates = rates["MORTGAGE30US"].resample("MS").mean().round(2)

monthly_rates = monthly_rates.reset_index()
monthly_rates["year_month"] = monthly_rates["observation_date"].dt.strftime("%Y-%m")
monthly_rates = monthly_rates[["year_month", "MORTGAGE30US"]].rename(columns={"MORTGAGE30US": "rate_30yr"})

print(monthly_rates[monthly_rates["year_month"] >= "2024-01"].to_string(index=False))

# Load cleaned Residential data
sold = pd.read_csv(os.path.join(OUTPUT_DIR, "sold_residential_eda.csv"), low_memory=False)
listing = pd.read_csv(os.path.join(OUTPUT_DIR, "listing_residential_eda.csv"), low_memory=False)

# Build year_month key: CloseDate for Sold, ListingContractDate for Listing
sold["year_month"] = pd.to_datetime(sold["CloseDate"]).dt.strftime("%Y-%m")
listing["year_month"] = pd.to_datetime(listing["ListingContractDate"]).dt.strftime("%Y-%m")

# Merge monthly rates onto each dataset
sold_rows_before = len(sold)
listing_rows_before = len(listing)

sold = sold.merge(monthly_rates, on="year_month", how="left")
listing = listing.merge(monthly_rates, on="year_month", how="left")

print(f"Sold rows: {sold_rows_before:,} before merge, {len(sold):,} after")
print(f"Listing rows: {listing_rows_before:,} before merge, {len(listing):,} after")

# Validation: no rate values should be null after the merge
sold_null_rates = sold["rate_30yr"].isna().sum()
listing_null_rates = listing["rate_30yr"].isna().sum()
print(f"Null rates after merge: Sold {sold_null_rates}, Listing {listing_null_rates}")

assert sold_null_rates == 0 and listing_null_rates == 0, "Some rows did not get a mortgage rate"

# Spot check: a few rows with their date, key and rate
print(sold[["CloseDate", "year_month", "rate_30yr"]].sample(5, random_state=1).to_string())

# Save enriched datasets
sold.to_csv(os.path.join(OUTPUT_DIR, "sold_residential_enriched.csv"), index=False)
listing.to_csv(os.path.join(OUTPUT_DIR, "listing_residential_enriched.csv"), index=False)
print(f"Saved sold: {sold.shape[0]:,} rows, {sold.shape[1]} columns")
print(f"Saved listing: {listing.shape[0]:,} rows, {listing.shape[1]} columns")