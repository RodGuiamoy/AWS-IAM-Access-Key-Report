import os
import pandas as pd
import chardet
from datetime import datetime

# List all files in the current working directory
files = os.listdir()

# Filter out the .csv files
csv_files = [file for file in files if file.endswith('.csv')]
csv_files.sort()  # This sorts the list in place

# Read each CSV file and store them in a list
dfs = []
for file in csv_files:
    with open(file, 'rb') as f:
        result = chardet.detect(f.read())  # Detect the encoding
        encoding = result['encoding']

    try:
        df = pd.read_csv(file, encoding=encoding)
        print(df)
        dfs.append(df)
    except Exception as e:
        # Show short description of the error
        print("An error occurred:", str(e))
    
# [pd.read_csv(file) for file in csv_files]

current_date = datetime.now().strftime('%m%d%Y')

# Create a new Excel writer object
writer = pd.ExcelWriter(f"AWS Console Access Report - {current_date}.xlsx", engine='xlsxwriter')

# Write each dataframe to a separate sheet in the Excel file, naming sheets after the filename
for i, df in enumerate(dfs):
    # Extract file name without the extension and use it as sheet name
    sheet_name = csv_files[i].rsplit('_', 1)[0]
    df.to_excel(writer, sheet_name=sheet_name, index=False)

# Save the Excel file
# writer.save()

# Ensure to close the writer object to avoid any warnings or errors
writer.close()

# Note: The 'FutureWarning' regarding the 'save' method in this context is specific to the version of pandas and xlsxwriter used in the example execution. 
# In a standard environment, make sure your libraries are up to date to minimize such warnings. Additionally, always close the ExcelWriter to release resources.
