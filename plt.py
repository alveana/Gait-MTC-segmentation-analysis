import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import find_peaks

input_file = "PreTest_LMTC_c3d.txt"
output_file = "PreTest_LMTC_c3d_Z_Displacement.xlsx"

# 1. Load the data
df = pd.read_csv(input_file, sep=r"\s+", engine="python", header=None,
                 names=["File", "Frame", "X", "Y", "Z", "Reliability"])

# 2. Convert and Clean
df['Frame'] = pd.to_numeric(df['Frame'], errors='coerce')
df['Z'] = pd.to_numeric(df['Z'], errors='coerce')
df.replace(-1.000000, np.nan, inplace=True)
filtered_df = df[["Frame", "Z"]].dropna().reset_index(drop=True)

# --- THE FIX: REMOVE THE INITIAL SPIKE ---
# We skip the first 50 frames (adjust if the spike lasts longer)
filtered_df = filtered_df.iloc[50:].reset_index(drop=True)

# Zero the displacement based on the new first frame
initial_z = filtered_df["Z"].iloc[0]
filtered_df["Vertical_Displacement"] = filtered_df["Z"] - initial_z
signal = filtered_df["Vertical_Displacement"].values

# 3. DETECT VALLEYS (Foot Strikes)
# Looking at your graph, the peaks are sharp and the valleys are distinct.
# Let's use a prominence of ~15-20% of the signal range.
dynamic_prominence = (np.max(signal) - np.min(signal)) * 0.2

valleys, _ = find_peaks(-signal, prominence=dynamic_prominence, distance=20)

# 4. DETECT PEAKS (Swing) BETWEEN VALLEYS
peaks = []
for i in range(len(valleys) - 1):
    start, end = valleys[i], valleys[i+1]
    peak_idx = np.argmax(signal[start:end]) + start
    peaks.append(peak_idx)
peaks = np.array(peaks)

# --- DATA PREP ---
peak_df = pd.DataFrame([{
    'Peak': i + 1, 'Frame': int(filtered_df["Frame"].iloc[p]), 'Displacement': float(signal[p])
} for i, p in enumerate(peaks)])

step_df = pd.DataFrame([{
    'Step': i + 1, 'Frame': int(filtered_df["Frame"].iloc[v]), 'Displacement': float(signal[v])
} for i, v in enumerate(valleys)])

# 5. Export
with pd.ExcelWriter(output_file) as writer:
    filtered_df.to_excel(writer, sheet_name='Displacement_Data', index=False)
    peak_df.to_excel(writer, sheet_name='Peaks', index=False)
    step_df.to_excel(writer, sheet_name='Steps', index=False)

# 6. Plotting
plt.figure(figsize=(15, 6))
plt.plot(filtered_df["Frame"], signal, color='#1a73e8', label='Z Displacement', alpha=0.7)
plt.scatter(filtered_df["Frame"].iloc[valleys], signal[valleys], color='green', s=40, label='Steps (Valleys)', zorder=5)
plt.scatter(filtered_df["Frame"].iloc[peaks], signal[peaks], color='red', marker='x', s=40, label='Peaks (Swing)', zorder=5)

plt.title(f"Gait Detection: {len(valleys)} Steps Found (Initial Spike Removed)")
plt.xlabel("Frame")
plt.ylabel("Vertical Displacement")
plt.legend()
plt.grid(True, linestyle=':', alpha=0.6)
plt.tight_layout()
plt.show()