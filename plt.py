import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import find_peaks

input_file = "PreTest_LMTC_c3d.txt"
output_file = "PreTest_LMTC_c3d_Z_Displacement.xlsx"

# 1. Load the data
df = pd.read_csv(input_file,
                 sep=r"\s+",
                 engine="python",
                 header=None,
                 names=["File", "Frame", "X", "Y", "Z", "Reliability"])

# 2. Convert columns to numeric
df['Frame'] = pd.to_numeric(df['Frame'], errors='coerce')
df['Z'] = pd.to_numeric(df['Z'], errors='coerce')

# 3. Handle missing values
df.replace(-1.000000, np.nan, inplace=True)

# 4. Filter and DROP rows with missing data
filtered_df = df[["Frame", "Z"]].dropna(subset=["Frame", "Z"]).copy()

initial_z = filtered_df["Z"].iloc[0]
filtered_df["Vertical_Displacement"] = filtered_df["Z"] - initial_z

# PEAK COUNTING LOGIC - detecting TOP of swing phase
peaks, _ = find_peaks(filtered_df["Vertical_Displacement"],
                       distance=38,
                       height=filtered_df["Vertical_Displacement"].mean())

# VALLEY DETECTION - detecting BOTTOM (foot strike) - THIS IS THE STEP
valleys, _ = find_peaks(-filtered_df["Vertical_Displacement"],  # Negative signal to find valleys
                         distance=38,
                         height=-filtered_df["Vertical_Displacement"].quantile(0.25))

peak_count = len(peaks)
step_count = len(valleys)  # Valleys represent actual steps

average_peak_disp = filtered_df["Vertical_Displacement"].iloc[peaks].mean()
average_step_disp = filtered_df["Vertical_Displacement"].iloc[valleys].mean()

# --- PEAK DATA: Frame number for each peak ---
peak_data = []
frame_values = filtered_df["Frame"].values

for i, peak_idx in enumerate(peaks):
    peak_data.append({
        'Peak': i + 1,
        'Frame': int(frame_values[peak_idx]),
        'Displacement': float(filtered_df["Vertical_Displacement"].iloc[peak_idx])
    })

peak_df = pd.DataFrame(peak_data)

# --- STEP DATA: Frame number for each step (valley) ---
step_data = []

for i, valley_idx in enumerate(valleys):
    step_data.append({
        'Step': i + 1,
        'Frame': int(frame_values[valley_idx]),
        'Displacement': float(filtered_df["Vertical_Displacement"].iloc[valley_idx])
    })

step_df = pd.DataFrame(step_data)

# 5. Export to Excel with three sheets
with pd.ExcelWriter(output_file) as writer:
    filtered_df.to_excel(writer, sheet_name='Displacement_Data', index=False)
    peak_df.to_excel(writer, sheet_name='Peaks', index=False)
    step_df.to_excel(writer, sheet_name='Steps', index=False)

print(f"Excel file created: {output_file}")
print(f"Total Peaks Counted: {peak_count}")
print(f"Total Steps Counted: {step_count}")
print(f"Average Peak Vertical Displacement: {average_peak_disp:.2f}")
print(f"Average Step Vertical Displacement: {average_step_disp:.2f}")

# --- COMBINED PEAKS AND STEPS TABLE ---
print("PEAKS AND STEPS")
print("=" * 110)
print(
    f"{'Peak #':<10} | {'Peak Frame':<15} | {'Peak Disp':<15} | {'Step #':<10} | {'Step Frame':<15} | {'Step Disp':<15}")
print("-" * 110)

# Combine the dataframes
for i in range(max(len(peak_df), len(step_df))):
    # Get peak data if available
    if i < len(peak_df):
        peak_num = peak_df.iloc[i]['Peak']
        peak_frame = peak_df.iloc[i]['Frame']
        peak_disp = f"{peak_df.iloc[i]['Displacement']:.2f}"
    else:
        peak_num = ""
        peak_frame = ""
        peak_disp = ""

    # Get step data if available
    if i < len(step_df):
        step_num = step_df.iloc[i]['Step']
        step_frame = step_df.iloc[i]['Frame']
        step_disp = f"{step_df.iloc[i]['Displacement']:.2f}"
    else:
        step_num = ""
        step_frame = ""
        step_disp = ""

    print(
        f"{str(peak_num):<10} | {str(peak_frame):<15} | {peak_disp:<15} | {str(step_num):<10} | {str(step_frame):<15} | {step_disp:<15}")
# 6. Plotting
try:
    plt.figure(figsize=(12, 5))

    # Plot the Displacement
    plt.plot(filtered_df["Frame"].values, filtered_df["Vertical_Displacement"].values,
             color='#1a73e8', linewidth=1, label='Vertical Displacement')

    # Mark each peak (swing phase)
    plt.plot(filtered_df["Frame"].iloc[peaks], filtered_df["Vertical_Displacement"].iloc[peaks],
             "rx", markersize=8, label=f'Peaks ({peak_count})')

    # Mark each STEP (foot strike at valley)
    plt.plot(filtered_df["Frame"].iloc[valleys], filtered_df["Vertical_Displacement"].iloc[valleys],
             "go", markersize=8, label=f'Steps ({step_count})')

    # Dashed line for the average peak height
    plt.axhline(y=average_peak_disp, color='red', linestyle='--', alpha=0.5,
                label=f'Avg Peak: {average_peak_disp:.2f}')

    # Dashed line for the average step depth
    plt.axhline(y=average_step_disp, color='green', linestyle='--', alpha=0.5,
                label=f'Avg Step: {average_step_disp:.2f}')

    plt.title(f"Vertical Displacement: {peak_count} Peaks, {step_count} Steps Detected", fontsize=14)
    plt.xlabel("Frames", fontsize=11)
    plt.ylabel("Displacement from Start", fontsize=11)
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.legend()

    plt.tight_layout()

    plt.savefig("Gait_Analysis_Plot.png", dpi=300)
    print("Graph saved as Gait_Analysis_Plot.png")
    plt.show()
except KeyboardInterrupt:
    print("\nPlot interrupted by user")
    plt.close('all')
finally:
    plt.close('all')
