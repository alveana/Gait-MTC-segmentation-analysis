import numpy as np
import pandas as pd

input_file = "PreTest_LMTC_c3d.txt"
output_file = "PreTest_LMTC_c3d_X_D.xlsx" # Changed extension to .xlsx

# Load the data
df = pd.read_csv(input_file,
                 sep=r"\s+",
                 engine="python",
                 header=None,
                 names=["File", "Frame", "X", "Y", "Z", "Reliability"])

# Handle missing values
df.replace(-1.000000, np.nan, inplace=True)

# Filter for only Frame and X
filtered_df = df[["Frame", "X"]]

# Export to Excel
# index=False prevents pandas from adding an extra column for row numbers
filtered_df.to_excel(output_file, index=False)

print(f"Data successfully exported to {output_file}")