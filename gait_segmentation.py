import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
import os

#Specifically for Pretest_LMTC.c3d and clean the data to be matched
class ReferenceDataProcessor:

    def __init__(self, file_path, steps_per_set=10):
        self.file_path = file_path
        self.steps_per_set = steps_per_set
        self.raw_data = None
        self.processed_data = None
        self.all_steps = []
        self.valid_steps = []
        self.step_labels = {}  # {frame: 'Adjusted' or 'Normal'}
        
    def load_data(self):
        #This step will load reference data from the file
        print(f"\n Loading reference data: {self.file_path}")
        
        self.raw_data = pd.read_csv(
            self.file_path,
            sep=r"\s+",
            engine="python",
            header=None,
            names=["File", "Frame", "X", "Y", "Z", "Reliability"]
        )
        
        print(f"✓ Loaded {len(self.raw_data)} rows")
        return self.raw_data
    
    def process_data(self):
        # Clean and prepare reference data
        print("\n Processing reference data...")

        # Convert to numeric
        df = self.raw_data.copy()
        df['Frame'] = pd.to_numeric(df['Frame'], errors='coerce')
        df['Z'] = pd.to_numeric(df['Z'], errors='coerce')

        # Handling and filtering missing values (typically -1.000000)
        df.replace(-1.000000, np.nan, inplace=True)
        df = df[["Frame", "Z"]].dropna(subset=["Frame", "Z"]).copy()
        
        # Calculate vertical displacement
        initial_z = df["Z"].iloc[0]
        df["Vertical_Displacement"] = df["Z"] - initial_z
        
        self.processed_data = df
        print(f"✓ Processed {len(df)} clean frames")
        return df

    def detect_steps(self):
        print("\n Detecting steps (Adaptive Windowing Method)...")

        # 1. Clean the initial spike (ignore first 50 frames for stability)
        # This prevents the Frame 0 jump from ruining your vertical scale
        if len(self.processed_data) > 50:
            df_clean = self.processed_data.iloc[50:].reset_index(drop=True)
        else:
            df_clean = self.processed_data.reset_index(drop=True)

        displacement = df_clean["Vertical_Displacement"].values
        frames = df_clean["Frame"].values
        # 2. Dynamic Thresholding:
        
        signal_std = np.std(displacement)
        valley_prominence = signal_std*0.5
        # 3. Dynamic Valley Detection (Foot Strikes)
        # We use prominence instead of distance.
        # A prominence of 20% of the signal range is usually the 'sweet spot'.
        signal_range = np.max(displacement) - np.min(displacement)
        valleys, _ = find_peaks(
            -displacement,
            prominence=valley_prominence,
            distance=15 # Minimum safety distance to avoid double-peaks
        )

        # 3. Finding Peaks (Swing Phase) BETWEEN Valleys
        # This makes the "Peak Distance" 100% dynamic to the user's pace.
        self.all_steps = []

        # We loop through valleys to find the high point (peak) between each strike
        for i in range(len(valleys) - 1):
            v_start = valleys[i]
            v_end = valleys[i + 1]

            # Find the max within this specific window (one gait cycle)
            window = displacement[v_start:v_end]
            if len(window) > 0:
                # np.argmax gives index relative to the window, so we add v_start
                peak_idx_relative = np.argmax(window)
                peak_idx_absolute = peak_idx_relative + v_start
                # Store step info relative to the valley that completes the step
                self.all_steps.append({
                    'step_number': i + 1,
                    'frame': int(frames[v_end]),  # Foot strike frame
                    'displacement': float(displacement[v_end]),
                    'peak_frame': int(frames[peak_idx_absolute]),  # Peak swing frame
                    'peak_displacement': float(displacement[peak_idx_relative]),
                    'array_index': v_end
                })

        print(f"✓ Detected {len(self.all_steps)} total dynamic gait cycles")
        return self.all_steps
    
    def group_and_label_steps(self):
        """
        Group steps into sets of 10 and assign labels.
        Set 1 (steps 1-10): Adjusted
        Set 2 (steps 11-20): Normal
        Set 3 (steps 21-30): Adjusted
        ... and so on (alternating)
        """
        print("\n Grouping steps into sets and assigning labels...")
        
        total_steps = len(self.all_steps)
        num_complete_sets = total_steps // self.steps_per_set
        
        sets_info = []
        
        for set_num in range(num_complete_sets):
            start_idx = set_num * self.steps_per_set
            end_idx = start_idx + self.steps_per_set
            
            set_steps = self.all_steps[start_idx:end_idx]
            
            # Alternate: Odd Sets = Adjusted & Even Sets = Normal
            condition = "Adjusted" if set_num % 2 == 0 else "Normal"
            
            sets_info.append({
                'set_number': set_num + 1,
                'condition': condition,
                'steps': set_steps,
                'start_step': start_idx + 1,
                'end_step': end_idx
            })
            
            print(f"  Set {set_num + 1}: Steps {start_idx + 1}-{end_idx} → {condition}")
        
        # Handle remaining steps (if any)
        remaining = total_steps % self.steps_per_set
        if remaining > 0:
            print(f"  Warning: {remaining} steps remaining (incomplete set, will be ignored)")
        
        return sets_info
    def label_all_steps(self, sets_info):
        print("\n Labeling all steps...")
        labeled_all_steps = []

        for set_info in sets_info:
            steps = set_info['steps']
            condition = set_info['condition']
            set_num = set_info['set_number']

            #Label ALL step (1-10) in this set
            for i, step in enumerate(steps):
                step_copy = step.copy()
                step_copy['condition'] = condition
                step_copy['set_number'] = set_num
                step_copy['position_in_set'] = i + 1 #Position 1-10
                labeled_all_steps.append(step_copy)

        self.all_steps = labeled_all_steps
        print(f" ✓ Labeled {len(self.all_steps)} steps with conditions")
        return self.all_steps

    def filter_valid_steps(self, sets_info):
        """
        Keep only steps 2-9 from each set (skip first and last).
        This removes transition/adjustment steps.
        """
        print("\n  Filtering to keep steps 2-9 from each set...")
        
        adjusted_count = 0
        normal_count = 0
        
        for set_info in sets_info:
            steps = set_info['steps']
            condition = set_info['condition']
            set_num = set_info['set_number']
            
            # Keep steps at indices 1-8 (steps 2-9 in the set)
            valid_steps_in_set = steps[1:9]
            
            for i, step in enumerate(valid_steps_in_set):
                step_copy = step.copy()
                step_copy['condition'] = condition
                step_copy['set_number'] = set_num
                step_copy['position_in_set'] = i + 2  # Focussing on Step Position 2-9
                
                self.valid_steps.append(step_copy)
                
                # Create frame -> label mapping
                self.step_labels[step['frame']] = condition
                
                if condition == "Adjusted":
                    adjusted_count += 1
                else:
                    normal_count += 1
        
        print(f" Kept {len(self.valid_steps)} valid steps:")
        print(f"   - Adjusted: {adjusted_count} steps")
        print(f"   - Normal: {normal_count} steps")
        
        return self.valid_steps
    
    def export_reference_summary(self, output_file="reference_step_labels.xlsx"):
        #Export reference step information to Excel
        print(f"\n Exporting reference summary...")
        df = pd.DataFrame(self.valid_steps)
        df = df[['step_number', 'frame', 'displacement', 'condition', 'set_number', 'position_in_set']]
        
        df.to_excel(output_file, index=False)
        print(f"  ✓ Saved: {output_file}")
        
        return output_file

    def export_reference_prefilters(self, output_file="prefiltered_reference_step_labels.xlsx"):
        #Check if label_al_step() was called first
        if len(self.all_steps) > 0 and 'condition' not in self.all_steps[0]:
            raise ValueError("Steps have not been labelled yet. Run label_all_steps first.")

        df = pd.DataFrame(self.all_steps)
        df = df[['frame', 'displacement', 'condition', 'set_number', 'position_in_set']]
        df.to_excel(output_file, index=False)
        print(f"  ✓ Saved: {output_file} ({len(df)} steps - complete sets)")
        return output_file

    def get_step_labels(self):
        #Return the frame -> condition mapping for matching
        return self.step_labels
    
    def run_full_processing(self):
        #Execute complete reference processing pipeline
        self.load_data()
        self.process_data()
        self.detect_steps()
        sets_info = self.group_and_label_steps()
        #Label ALL steps (1-10) with condition and set info
        self.label_all_steps(sets_info)
        #Export prefiltered data (all steps 1-10 with labels)
        self.export_reference_prefilters()
        #Filter to steps 2-9
        self.filter_valid_steps(sets_info)
        #Export filtered steps (2-9 only)
        self.export_reference_summary()
        
        return self.step_labels


class AngleDataProcessor:
    #Processes a single angle data file and matches it to reference step labels.
    #NO step detection needed - just frame matching.

    
    def __init__(self, file_path, reference_step_labels):
        self.file_path = file_path
        self.reference_step_labels = reference_step_labels  # {frame: condition}
        self.raw_data = None
        self.processed_data = None
        self.labeled_data = None
        
    def load_data(self):
        #Load angle data from file
        angle_name = os.path.basename(self.file_path)
        print(f"\n Loading angle data: {angle_name}")
        
        self.raw_data = pd.read_csv(
            self.file_path,
            sep=r"\s+",
            engine="python",
            header=None,
            names=["File", "Frame", "X", "Y", "Z", "Reliability"]
        )
        
        print(f"  ✓ Loaded {len(self.raw_data)} rows")
        return self.raw_data
    
    def process_data(self):

        print("\n Processing new angle data...")
        
        # Convert to numeric
        df = self.raw_data.copy()
        df['Frame'] = pd.to_numeric(df['Frame'], errors='coerce')
        df['Z'] = pd.to_numeric(df['Z'], errors='coerce')
        
        # Handle and filters missing values
        df.replace(-1.000000, np.nan, inplace=True)
        df = df[["Frame", "X", "Y", "Z", "Reliability"]].dropna(subset=["Frame"]).copy()
        
        # Calculate angle displacement (if needed)
        if 'Z' in df.columns:
            initial_z = df["Z"].iloc[0]
            df["Z_Displacement"] = df["Z"] - initial_z
        
        self.processed_data = df
        print(f"   ✓ Processed {len(df)} clean frames")
        return df
    
    def match_to_reference(self):

        #Match angle frames to reference step labels.
        #Since frames are synchronized, direct frame number matching.

        print("\n Matching frames to reference labels...")
        
        # Create a copy for labeling
        self.labeled_data = self.processed_data.copy()
        self.labeled_data['Condition'] = 'Unknown'
        
        # Match each frame to reference labels
        matched_adjusted = 0
        matched_normal = 0
        unmatched = 0
        
        for idx, row in self.labeled_data.iterrows():
            frame = int(row['Frame'])
            
            if frame in self.reference_step_labels:
                condition = self.reference_step_labels[frame]
                self.labeled_data.at[idx, 'Condition'] = condition
                
                if condition == 'Adjusted':
                    matched_adjusted += 1
                else:
                    matched_normal += 1
            else:
                unmatched += 1
        
        print(f"   ✓ Frame matching complete:")
        print(f"     - Adjusted frames: {matched_adjusted}")
        print(f"     - Normal frames: {matched_normal}")
        print(f"     - Unmatched frames: {unmatched}")
        
        return self.labeled_data
    
    def separate_by_condition(self):
        #Splitting data into Adjusted and Normal dataframes
        print("\n  Separating data by condition...")
        
        adjusted_data = self.labeled_data[self.labeled_data['Condition'] == 'Adjusted'].copy()
        normal_data = self.labeled_data[self.labeled_data['Condition'] == 'Normal'].copy()
        
        print(f"   ✓ Adjusted: {len(adjusted_data)} frames")
        print(f"   ✓ Normal: {len(normal_data)} frames")
        
        return adjusted_data, normal_data
    
    def export_separated_data(self, base_filename):
        #Export separate Excel files for Adjusted and Normal conditions
        print("\n Exporting adjusted vs normal step data seperately...")
        
        adjusted_data, normal_data = self.separate_by_condition()
        
        # Create filenames
        adjusted_file = f"{base_filename}_adjusted_steps.xlsx"
        normal_file = f"{base_filename}_normal_steps.xlsx"
        
        # Export to Excel
        adjusted_data.to_excel(adjusted_file, index=False)
        normal_data.to_excel(normal_file, index=False)
        
        print(f"  ✓ Saved: {adjusted_file} ({len(adjusted_data)} rows)")
        print(f"  ✓ Saved: {normal_file} ({len(normal_data)} rows)")
        
        return adjusted_file, normal_file
    
    def run_full_processing(self, base_filename):
        #Execute complete angle processing pipeline
        self.load_data()
        self.process_data()
        self.match_to_reference()
        files = self.export_separated_data(base_filename)
        
        return files


class GaitSegmentationPipeline:
    #Main orchestrator for the complete gait segmentation workflow.
    #Processes one angle file at a time.

    
    def __init__(self, reference_file):
        self.reference_file = reference_file
        self.reference_processor = None
        self.reference_step_labels = None
    
    def process_reference(self):
        #Step 1: Process reference LMTC data to establish ground truth.
        print("\n" + "="*70)
        print("STEP 1: PROCESSING REFERENCE DATA (PreTest_LMTC_c3d)")
        print("="*70)
        
        self.reference_processor = ReferenceDataProcessor(
            self.reference_file,
            steps_per_set=10
        )
        
        self.reference_step_labels = self.reference_processor.run_full_processing()
        
        print("\n Reference processing complete!")
        print(f"   Total labeled frames: {len(self.reference_step_labels)}")
        
        return self.reference_step_labels
    
    def process_angle_file(self, angle_file):
        """
        Step 2: Process a single angle file and match to reference.
        
        Parameters:
        -----------
        angle_file : str
            Path to angle data file (e.g., "hip_angle.txt")
        """
        # Check if reference has been processed
        if self.reference_step_labels is None:
            raise ValueError("Must process reference data first! Call process_reference()")
        
        # Extract base filename for outputs
        base_filename = os.path.splitext(os.path.basename(angle_file))[0]
        
        print("\n" + "="*70)
        print(f"STEP 2: PROCESSING ANGLE DATA ({base_filename})")
        print("="*70)
        
        # Process angle data
        angle_processor = AngleDataProcessor(
            angle_file,
            self.reference_step_labels
        )
        
        output_files = angle_processor.run_full_processing(base_filename)
        
        print("\n Angle processing complete!")
        print(f"   Output files: {output_files[0]}, {output_files[1]}")
        
        return output_files
    
    def run_complete_pipeline(self, angle_file):
        """
        Run both reference and angle processing in sequence.
        
        Parameters:
        -----------
        angle_file : str
            Path to angle data file
        """
        print("GAIT SEGMENTATION PIPELINE")
        print("Adjusted vs Normal Classification")
        
        # Process reference
        self.process_reference()
        
        # Process angle file
        output_files = self.process_angle_file(angle_file)
        
        print("\n" + "="*70)
        print(" PIPELINE COMPLETE!")
        print("="*70)
        print("\nGenerated files:")
        print("  1. reference_step_labels.xlsx")
        print(f"  2. {output_files[0]}")
        print(f"  3. {output_files[1]}")
        print("\n")
        
        return output_files
