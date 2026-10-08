# Weeks 2-3, Deliverable Set 1: Validation and EDA


# Inputing libraries and Verifying filter 

import pandas as pd
import os

OUTPUT_DIR = r"C:\Users\abdif\IDX_Data\output"

sold = pd.read_csv(os.path.join(OUTPUT_DIR, "sold_residential_202401_202604.csv"), low_memory=False)
listing = pd.read_csv(os.path.join(OUTPUT_DIR, "listing_residential_202401_202604.csv"), low_memory=False)

print(sold["PropertyType"].unique())
print(listing["PropertyType"].unique())
# PropertyType values found: Residential, ResidentialLease, Land, ManufacturedInPark, ResidentialIncome, CommercialSale, CommercialLease, BusinessOpportunity (no blanks)
# Filter: PropertyType == "Residential" (exact match). Excludes ResidentialLease (rentals) and ResidentialIncome (multi-unit), which would distort sale prices.


print(f"Sold: {sold.shape[0]:,} rows, {sold.shape[1]} columns")
print(f"Listing: {listing.shape[0]:,} rows, {listing.shape[1]} columns")

print(sold.dtypes.value_counts())
print(sold.dtypes.to_string())
# Market fields: price, size/features, dates, DOM, location, agent/office names
# Metadata: IDs, system fields, MlsStatus, latfilled/lonfilled. Dates stored as text.

# Null-count summary table

def null_summary(df):
    missing_count = df.isna().sum()
    missing_pct = (missing_count / len(df) * 100).round(2)
    table = pd.DataFrame({"missing_count": missing_count, "missing_pct": missing_pct})
    return table.sort_values("missing_pct", ascending=False)

sold_nulls = null_summary(sold)
listing_nulls = null_summary(listing)

print("SOLD null summary")
print(sold_nulls.to_string())
print("LISTING null summary")
print(listing_nulls.to_string())

# Verify Listing duplicate columns before dropping

dup_cols = [col for col in listing.columns if col.endswith(".1")]

for dup in dup_cols:
    original = dup[:-2]
    same = listing[original].equals(listing[dup])
    diff_rows = (listing[original] != listing[dup]) & ~(listing[original].isna() & listing[dup].isna())
    print(f"{original}: identical={same}, rows that differ={diff_rows.sum()}")


# Inspect the 2 pairs that differ
for original in ["BuyerOfficeName", "UnparsedAddress"]:
    dup = original + ".1"
    mask = (listing[original] != listing[dup]) & ~(listing[original].isna() & listing[dup].isna())
    print(listing.loc[mask, ["ListingKey", original, dup]].to_string())

# Drop duplicate .1 columns (verified: 9 identical, 2 differ only in ListingKey 1151935665, where the .1 copy is truncated/blank and the original is correct)
listing = listing.drop(columns=dup_cols)
print(f"Listing after dropping duplicates: {listing.shape[1]} columns")

# Missing value report: flag columns over 90% missing
listing_nulls = null_summary(listing) 
sold_flagged = sold_nulls[sold_nulls["missing_pct"] > 90]
listing_flagged = listing_nulls[listing_nulls["missing_pct"] > 90]
print(f"SOLD: {len(sold_flagged)} columns over 90% missing")
print(sold_flagged.to_string())
print(f"LISTING: {len(listing_flagged)} columns over 90% missing")
print(listing_flagged.to_string())


# Drop all >90% missing columns
sold = sold.drop(columns=sold_flagged.index)
listing = listing.drop(columns=listing_flagged.index)

print(f"Sold after dropping >90% missing: {sold.shape[1]} columns")
print(f"Listing after dropping >90% missing: {listing.shape[1]} columns")

# Numeric distribution summary (Sold: ClosePrice is only meaningful for closed sales)
pd.set_option("display.float_format", "{:,.2f}".format)

summary = sold[["ClosePrice", "LivingArea", "DaysOnMarket"]].describe(
    percentiles=[0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99]
)
print(summary.to_string())



# Listing status breakdown and repeat listings
print(listing["MlsStatus"].value_counts(dropna=False))

repeat_keys = listing["ListingKey"].duplicated().sum()
print(f"Listing rows whose ListingKey appears more than once: {repeat_keys:,}")


# Save filtered datasets (Residential, duplicate columns removed, >90%-missing columns dropped)
sold.to_csv(os.path.join(OUTPUT_DIR, "sold_residential_eda.csv"), index=False)
listing.to_csv(os.path.join(OUTPUT_DIR, "listing_residential_eda.csv"), index=False)
sold_nulls.to_csv(os.path.join(OUTPUT_DIR, "sold_null_summary.csv"))
listing_nulls.to_csv(os.path.join(OUTPUT_DIR, "listing_null_summary.csv"))

print(f"Saved sold: {sold.shape[0]:,} rows, {sold.shape[1]} columns")
print(f"Saved listing: {listing.shape[0]:,} rows, {listing.shape[1]} columns")