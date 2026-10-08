# Week 1: Aggregate monthly CRMLS Sold and Listing files (Jan 2024 – Apr 2026)
# 1. Concatenate all monthly files into one Sold and one Listing dataset
# 2. Filter both to PropertyType == 'Residential'
# 3. Save as new CSVs, recording row counts at each step


#  Import necessary libraries

import pandas as pd # Loads Pandas library
import os

DATA_DIR = r"C:\Users\abdif\IDX_Data\csv" # Stores folder path as a variable

files = os.listdir(DATA_DIR) # Asks os module to list every file and folder name in directory
print(files)


# Find Files

import glob  # Loads Python tool for finding files and folders

sold_path = sorted(glob.glob(os.path.join(DATA_DIR, "CRMLSSold*.csv"))) # Builds search path for sold houses and sorts the list of files in ascending order
listing_path = sorted(glob.glob(os.path.join(DATA_DIR, "CRMLSListing*.csv"))) # Builds search path for listing houses and sorts the list of files in ascending order

print(f"Sold files: {len(sold_path)}") # Prints the number of sold files in the directory
print(f"Listing files: {len(listing_path)}") # Prints the number of listing files in the directory

#  Read and concatenate sold datasets

sold_frames = [] # Empty list to hold one DataFrame per monthly Sold file
sold_frames_before = 0 # Running total of rows across all Sold files (before concat)

for path in sold_path:
    df = pd.read_csv(path, low_memory = False) # Loads each sold dataset into a dataframe
    sold_frames_before += len(df) # Adds the number of rows in each dataframe to the total count
    sold_frames.append(df) # Appends each dataframe to the list

sold = pd.concat(sold_frames, ignore_index = True) # Concatenates all dataframes in the list into a single dataframe and resets the index

print(f"Sold rows before concat (sum of all files): {sold_frames_before}") # Prints the total number of rows in all sold datasets before concatenation
print(f"Sold rows after concat: {len(sold)}") # Prints the number of rows in the concatenated sold dataframe

listing_frames = [] # Empty list to hold one DataFrame per monthly Listing file
listing_frames_before = 0  

for path in listing_path:
    df = pd.read_csv(path, low_memory = False) # Loads each listing dataset into a dataframe
    listing_frames_before += len(df) # Adds the number of rows in each dataframe to the total count
    listing_frames.append(df) # Appends each dataframe to the list

listing = pd.concat(listing_frames, ignore_index = True) # Concatenates all dataframes in the list into a single dataframe and resets the index

print(f"Listing rows before concat (sum of all files): {listing_frames_before}") # Prints the total number of rows in all listing datasets before concatenation
print(f"Listing rows after concat: {len(listing)}") # Prints the number of rows in the concatenated listing dataframe


# Filter

print(sold["PropertyType"].value_counts(dropna=False))  # Finding out what values exists
print(listing["PropertyType"].value_counts(dropna=False))

sold_res = sold[sold["PropertyType"] == "Residential"] # Filters the sold dataframe to only include rows where PropertyType is Residential
listing_res = listing[listing["PropertyType"] == "Residential"] # Filters the listing dataframe


print(f"Sold rows before filter: {len(sold):,}")
print(f"Sold rows after Residential filter: {len(sold_res):,}")
print(f"Listing rows before filter: {len(listing):,}")
print(f"Listing rows after Residential filter: {len(listing_res):,}")

# Row counts:
#   Sold: 615,707 rows before concat, 615,707 after concat, and 414,054 after Residential filter
#   Listing: 860,898 rows before concat, 860,898 after concat, and 547,162 after Residential filter 

# Save

OUTPUT_DIR = r"C:\Users\abdif\IDX_Data\output"  # Separate folder for results, not mixed with raw files
os.makedirs(OUTPUT_DIR, exist_ok=True)           # Creates the folder; no error if it already exists

sold_res.to_csv(os.path.join(OUTPUT_DIR, "sold_residential_202401_202604.csv"), index=False)
listing_res.to_csv(os.path.join(OUTPUT_DIR, "listing_residential_202401_202604.csv"), index=False)

print(f"Saved both files to {OUTPUT_DIR}")

print(len(pd.read_csv(os.path.join(OUTPUT_DIR, "sold_residential_202401_202604.csv"), low_memory=False)))
print(len(pd.read_csv(os.path.join(OUTPUT_DIR, "listing_residential_202401_202604.csv"), low_memory=False)))

