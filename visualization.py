#Visualization Module for Gait Segmentation
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


class GaitVisualizer:

    #Creates visualizations for gait segmentation analysis.
    
    @staticmethod
    def plot_reference_segmentation(processor, save_file="reference_segmentation.png"):

        #Visualize reference data with step detection and labels.
        #Parameters:
        #processor : ReferenceDataProcessor The processor object after running full processing
        #save_file : str Filename to save the plot
        
        if processor.processed_data is None or not processor.valid_steps:
            raise ValueError("Processor must be run first!")
        
        # Get data
        frames = processor.processed_data["Frame"].values
        displacement = processor.processed_data["Vertical_Displacement"].values
        
        # Create figure
        fig, ax = plt.subplots(figsize=(16, 6))
        
        # Plot displacement
        ax.plot(frames, displacement, 'b-', linewidth=1, alpha=0.6, label='Vertical Displacement')
        
        # Mark all detected steps
        for step in processor.all_steps:
            frame = step['frame']
            idx = step['array_index']
            ax.plot(frame, displacement[idx], 'ko', markersize=4, alpha=0.3)
        
        # Highlight valid steps with colors
        adjusted_frames = []
        adjusted_disps = []
        normal_frames = []
        normal_disps = []
        
        for step in processor.valid_steps:
            frame = step['frame']
            idx = step['array_index']
            
            if step['condition'] == 'Adjusted':
                adjusted_frames.append(frame)
                adjusted_disps.append(displacement[idx])
            else:
                normal_frames.append(frame)
                normal_disps.append(displacement[idx])
        
        # Plot with different colors
        ax.plot(adjusted_frames, adjusted_disps, 'r^', markersize=10, 
                label=f'Adjusted Steps ({len(adjusted_frames)})', 
                markeredgecolor='darkred', markeredgewidth=1.5)
        ax.plot(normal_frames, normal_disps, 'gv', markersize=10, 
                label=f'Normal Steps ({len(normal_frames)})', 
                markeredgecolor='darkgreen', markeredgewidth=1.5)
        
        # Add set boundaries
        for i in range(0, len(processor.all_steps), processor.steps_per_set):
            if i > 0:
                boundary_frame = processor.all_steps[i]['frame']
                ax.axvline(x=boundary_frame, color='gray', linestyle='--', 
                          alpha=0.3, linewidth=1)
        
        # Labels and formatting
        ax.set_xlabel('Frame Number', fontsize=12, fontweight='bold')
        ax.set_ylabel('Vertical Displacement (mm)', fontsize=12, fontweight='bold')
        ax.set_title('Reference Data: Step Segmentation and Classification\n' + 
                    'Steps 2-9 from each set labeled as Adjusted (red) or Normal (green)',
                    fontsize=14, fontweight='bold', pad=20)
        ax.legend(loc='best', fontsize=10)
        ax.grid(True, alpha=0.3, linestyle=':')
        
        plt.tight_layout()
        plt.savefig(save_file, dpi=300, bbox_inches='tight')
        print(f"\n Visualization saved: {save_file}")
        
        return fig
    
    @staticmethod
    def plot_angle_matching(angle_processor, angle_name="Angle", save_file=None):
        """
        Visualize angle data with matched labels.
        
        Parameters:
        -----------
        angle_processor : AngleDataProcessor
            The processor object after running full processing
        angle_name : str
            Name of the angle being visualized
        save_file : str
            Filename to save the plot (optional)
        """
        
        if angle_processor.labeled_data is None:
            raise ValueError("Angle processor must be run first!")
        
        # Get data
        data = angle_processor.labeled_data
        
        adjusted_data = data[data['Condition'] == 'Adjusted']
        normal_data = data[data['Condition'] == 'Normal']
        unmatched_data = data[data['Condition'] == 'Unknown']
        
        # Create figure
        fig, ax = plt.subplots(figsize=(16, 6))
        
        # Plot based on what data is available
        if 'Z_Displacement' in data.columns:
            y_col = 'Z_Displacement'
            y_label = 'Z Displacement'
        elif 'Z' in data.columns:
            y_col = 'Z'
            y_label = 'Z Value'
        else:
            print("  No suitable column found for plotting")
            return None
        
        # Plot unmatched (background)
        if len(unmatched_data) > 0:
            ax.scatter(unmatched_data['Frame'], unmatched_data[y_col], 
                      c='lightgray', s=20, alpha=0.3, label='Unmatched')
        
        # Plot adjusted
        if len(adjusted_data) > 0:
            ax.scatter(adjusted_data['Frame'], adjusted_data[y_col],
                      c='red', s=30, alpha=0.7, marker='^',
                      label=f'Adjusted ({len(adjusted_data)} frames)',
                      edgecolors='darkred', linewidths=0.5)
        
        # Plot normal
        if len(normal_data) > 0:
            ax.scatter(normal_data['Frame'], normal_data[y_col],
                      c='green', s=30, alpha=0.7, marker='v',
                      label=f'Normal ({len(normal_data)} frames)',
                      edgecolors='darkgreen', linewidths=0.5)
        
        # Labels and formatting
        ax.set_xlabel('Frame Number', fontsize=12, fontweight='bold')
        ax.set_ylabel(y_label, fontsize=12, fontweight='bold')
        
        match_rate = (len(adjusted_data) + len(normal_data)) / len(data) * 100
        ax.set_title(f'{angle_name} Data: Frame Matching to Reference Labels\n' +
                    f'Match Rate: {match_rate:.1f}%',
                    fontsize=14, fontweight='bold', pad=20)
        
        ax.legend(loc='best', fontsize=10)
        ax.grid(True, alpha=0.3, linestyle=':')
        
        plt.tight_layout()
        
        if save_file:
            plt.savefig(save_file, dpi=300, bbox_inches='tight')
            print(f"\n Visualization saved: {save_file}")
        
        return fig
    
    @staticmethod
    def plot_comparison(adjusted_file, normal_file, angle_name="Angle"):
        """
        Create side-by-side comparison of adjusted vs normal conditions.
        
        Parameters:
        -----------
        adjusted_file : str
            Path to adjusted steps Excel file
        normal_file : str
            Path to normal steps Excel file
        angle_name : str
            Name of the angle being compared
        """
        
        # Load data
        adjusted_df = pd.read_excel(adjusted_file)
        normal_df = pd.read_excel(normal_file)
        
        # Determine which column to plot
        if 'Z_Displacement' in adjusted_df.columns:
            y_col = 'Z_Displacement'
            y_label = 'Z Displacement'
        elif 'Z' in adjusted_df.columns:
            y_col = 'Z'
            y_label = 'Z Value'
        else:
            print("  No suitable column found for plotting")
            return None
        
        # Create figure with subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        
        # Plot Adjusted
        ax1.plot(adjusted_df['Frame'], adjusted_df[y_col], 
                'r-', linewidth=1.5, alpha=0.7)
        ax1.scatter(adjusted_df['Frame'], adjusted_df[y_col],
                   c='red', s=30, alpha=0.6, edgecolors='darkred')
        ax1.set_xlabel('Frame Number', fontsize=11, fontweight='bold')
        ax1.set_ylabel(y_label, fontsize=11, fontweight='bold')
        ax1.set_title(f'ADJUSTED Walking\n({len(adjusted_df)} frames)',
                     fontsize=12, fontweight='bold', color='darkred')
        ax1.grid(True, alpha=0.3, linestyle=':')
        
        # Plot Normal
        ax2.plot(normal_df['Frame'], normal_df[y_col],
                'g-', linewidth=1.5, alpha=0.7)
        ax2.scatter(normal_df['Frame'], normal_df[y_col],
                   c='green', s=30, alpha=0.6, edgecolors='darkgreen')
        ax2.set_xlabel('Frame Number', fontsize=11, fontweight='bold')
        ax2.set_ylabel(y_label, fontsize=11, fontweight='bold')
        ax2.set_title(f'NORMAL Walking\n({len(normal_df)} frames)',
                     fontsize=12, fontweight='bold', color='darkgreen')
        ax2.grid(True, alpha=0.3, linestyle=':')
        
        # Main title
        fig.suptitle(f'{angle_name}: Adjusted vs Normal Comparison',
                    fontsize=14, fontweight='bold', y=1.02)
        
        plt.tight_layout()
        
        save_file = f"{angle_name}_comparison.png"
        plt.savefig(save_file, dpi=300, bbox_inches='tight')
        print(f"\n Comparison visualization saved: {save_file}")
        
        return fig
    
    @staticmethod
    def create_summary_statistics(adjusted_file, normal_file, angle_name="Angle"):
        """
        Create a statistical summary table comparing adjusted vs normal.
        
        Parameters:
        -----------
        adjusted_file : str
            Path to adjusted steps Excel file
        normal_file : str
            Path to normal steps Excel file
        angle_name : str
            Name of the angle being analyzed
        """
        
        # Load data
        adjusted_df = pd.read_excel(adjusted_file)
        normal_df = pd.read_excel(normal_file)
        
        # Determine which column to analyze
        if 'Z_Displacement' in adjusted_df.columns:
            value_col = 'Z_Displacement'
        elif 'Z' in adjusted_df.columns:
            value_col = 'Z'
        else:
            print("  No suitable column found for analysis")
            return None
        
        # Calculate statistics
        stats = {
            'Metric': [
                'Number of Frames',
                'Mean',
                'Std Dev',
                'Min',
                'Max',
                'Range',
                '25th Percentile',
                'Median',
                '75th Percentile'
            ],
            'Adjusted': [
                len(adjusted_df),
                adjusted_df[value_col].mean(),
                adjusted_df[value_col].std(),
                adjusted_df[value_col].min(),
                adjusted_df[value_col].max(),
                adjusted_df[value_col].max() - adjusted_df[value_col].min(),
                adjusted_df[value_col].quantile(0.25),
                adjusted_df[value_col].median(),
                adjusted_df[value_col].quantile(0.75)
            ],
            'Normal': [
                len(normal_df),
                normal_df[value_col].mean(),
                normal_df[value_col].std(),
                normal_df[value_col].min(),
                normal_df[value_col].max(),
                normal_df[value_col].max() - normal_df[value_col].min(),
                normal_df[value_col].quantile(0.25),
                normal_df[value_col].median(),
                normal_df[value_col].quantile(0.75)
            ]
        }
        
        stats_df = pd.DataFrame(stats)
        
        # Calculate difference
        stats_df['Difference'] = stats_df['Normal'] - stats_df['Adjusted']
        stats_df.loc[0, 'Difference'] = np.nan  # Don't subtract counts
        
        # Print to console
        print(f"\n{'='*70}")
        print(f"STATISTICAL SUMMARY: {angle_name}")
        print(f"{'='*70}\n")
        print(stats_df.to_string(index=False))
        print(f"\n{'='*70}\n")
        
        # Save to Excel
        output_file = f"{angle_name}_statistics.xlsx"
        stats_df.to_excel(output_file, index=False)
        print(f" Statistics saved: {output_file}\n")
        
        return stats_df


# ============================================================================
# USAGE EXAMPLE
# ============================================================================

if __name__ == "__main__":

    print("VISUALIZATION EXAMPLES")
    
    # Example 1: Visualize reference segmentation
    print("Example 1: Visualizing reference segmentation...")
    from gait_segmentation import ReferenceDataProcessor
    
    processor = ReferenceDataProcessor("PreTest_LMTC_c3d.txt")
    processor.run_full_processing()
    
    GaitVisualizer.plot_reference_segmentation(processor)
    plt.show()
    
    
    # Example 2: Visualize angle matching
    print("\n Example 2: Visualizing angle data matching...")
    from gait_segmentation import AngleDataProcessor
    
    angle_proc = AngleDataProcessor("hip_angle.txt", processor.get_step_labels())
    angle_proc.run_full_processing("hip_angle")
    
    GaitVisualizer.plot_angle_matching(angle_proc, "Hip Angle", "hip_angle_matching.png")
    plt.show()
    
    
    # Example 3: Create comparison plot
    print("\n Example 3: Creating comparison visualization...")
    GaitVisualizer.plot_comparison(
        "hip_angle_adjusted_steps.xlsx",
        "hip_angle_normal_steps.xlsx",
        "Hip Angle"
    )
    plt.show()
    
    
    # Example 4: Generate statistics
    print("\n Example 4: Generating statistical summary...")
    GaitVisualizer.create_summary_statistics(
        "hip_angle_adjusted_steps.xlsx",
        "hip_angle_normal_steps.xlsx",
        "Hip Angle"
    )
    
    print("\n All visualizations complete!")
