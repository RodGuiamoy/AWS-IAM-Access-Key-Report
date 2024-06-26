import os
import pandas as pd
import chardet
from datetime import datetime

# List all files in the current working directory
files = os.listdir()

# Filter out the .csv files
# csv_files = [file for file in files if file.endswith('.csv')]
csv_files = [file for file in files if file.endswith('.csv') and not file.startswith('AWS Access Key Report')]

csv_files.sort()  # Sort the list in place

# Initialize an empty list to store dataframes
dfs = []

# Read each CSV file and store them in a list
for file in csv_files:
    with open(file, 'rb') as f:
        result = chardet.detect(f.read())  # Detect the encoding
        encoding = result['encoding']

    try:
        df = pd.read_csv(file, encoding=encoding)
        print(f"Successfully read {file}")
        dfs.append(df)
    except Exception as e:
        # Show a short description of the error
        print(f"An error occurred with file {file}: {str(e)}")

# Combine all dataframes into one
if dfs:
    combined_df = pd.concat(dfs, ignore_index=True)
    
    current_date = datetime.now().strftime('%m%d%Y')
    
    # Output filename
    output_file = f"AWS Access Key Report - {current_date}.csv"
    
    # Write the combined dataframe to a CSV file
    try:
        combined_df.to_csv(output_file, index=False)
        print(f"Combined CSV file '{output_file}' has been created successfully.")
    except Exception as e:
        print(f"An error occurred while writing to CSV: {str(e)}")
else:
    print("No CSV files were read successfully.")
