#Usage Script for Gait Segmentation Pipeline
from gait_segmentation import GaitSegmentationPipeline

def main():
    # Update these paths to match your files
    reference_file = "PreTest_LMTC_c3d.txt"
    angle_file = "LeftAnkle_Angle.txt"  # Process ONE angle file at a time
    
    # Running the Pipeline
    print("GAIT SEGMENTATION ANALYSIS")
    print("Processing: Reference + One Angle File")
    
    # Create pipeline
    pipeline = GaitSegmentationPipeline(reference_file)
    
    # Run complete analysis
    output_files = pipeline.run_complete_pipeline(angle_file)

    print("RESULTS SUMMARY")

    print("\nAnalysis complete! Generated files:")
    print(f"   1. reference_step_labels.xlsx")
    print(f"   2. {output_files[0]}")
    print(f"   3. {output_files[1]}")
    


'''def process_multiple_angles():
    """
    Process reference once, then multiple angle files one at a time.
    Recommended workflow for efficiency.
    """
    
    # ========== CONFIGURATION ==========
    reference_file = "PreTest_LMTC_c3d.txt"
    
    # List all angle files you want to process
    angle_files = [
        "hip_angle.txt",
        "knee_angle.txt", 
        "ankle_angle.txt"
    ]
    
    # RUN PIPELINE 
    print("BATCH PROCESSING: Multiple Angle Files")
  
    
    # Create pipeline
    pipeline = GaitSegmentationPipeline(reference_file)
    
    # Process reference ONCE
    print("="*70)
    print("PROCESSING REFERENCE DATA (only once)")
    print("="*70)
    pipeline.process_reference()
    
    # Process each angle file
    all_results = []
    
    for i, angle_file in enumerate(angle_files, 1):
        print(f"\n\n{'='*70}")
        print(f"PROCESSING ANGLE FILE {i}/{len(angle_files)}: {angle_file}")
        print("="*70)
        
        try:
            output_files = pipeline.process_angle_file(angle_file)
            all_results.append({
                'angle_file': angle_file,
                'status': 'Success',
                'outputs': output_files
            })
            print(f" {angle_file} processed successfully!")
            
        except Exception as e:
            print(f" Error processing {angle_file}: {e}")
            all_results.append({
                'angle_file': angle_file,
                'status': 'Failed',
                'error': str(e)
            })
    
    # ========== SUMMARY ==========
    print("\n\n" + "="*70)
    print("BATCH PROCESSING COMPLETE")
    print("="*70)
    
    print("\n Summary:")
    successful = sum(1 for r in all_results if r['status'] == 'Success')
    failed = sum(1 for r in all_results if r['status'] == 'Failed')
    
    print(f"  Successful: {successful}/{len(angle_files)}")
    print(f"  Failed: {failed}/{len(angle_files)}")
    
    print("\n Generated files:")
    print("   1. reference_step_labels.xlsx")
    
    for i, result in enumerate(all_results, 2):
        if result['status'] == 'Success':
            print(f"   {i}. {result['outputs'][0]}")
            print(f"   {i+1}. {result['outputs'][1]}")
    
    print("\n")


def verify_reference_only():
    
    reference_file = "PreTest_LMTC_c3d.txt"

    print("VERIFICATION MODE: Reference Data Only")

    from gait_segmentation import ReferenceDataProcessor
    
    # Process reference
    processor = ReferenceDataProcessor(reference_file, steps_per_set=10)
    
    processor.load_data()
    processor.process_data()
    all_steps = processor.detect_steps()
    sets = processor.group_and_label_steps()
    valid_steps = processor.filter_valid_steps(sets)
    processor.export_reference_summary()
    
    # Summary
    print("\n" + "="*70)
    print("VERIFICATION SUMMARY")
    print("="*70)
    
    print(f"\n✓ Total steps detected: {len(all_steps)}")
    print(f"✓ Number of complete sets: {len(sets)}")
    print(f"✓ Valid steps (2-9 per set): {len(valid_steps)}")
    
    adjusted = sum(1 for s in valid_steps if s['condition'] == 'Adjusted')
    normal = sum(1 for s in valid_steps if s['condition'] == 'Normal')
    
    print(f"\n✓ Adjusted steps: {adjusted}")
    print(f"✓ Normal steps: {normal}")
    
    print("\n Check 'reference_step_labels.xlsx' to verify labels are correct!")
    print("   If everything looks good, proceed with angle processing.\n")'''


# Run the script

if __name__ == "__main__":
    
    # Choose which mode to run:
    
    # MODE 1: Process reference + ONE angle file (simplest)
    # Uncomment the line below:
    main()
    
    
    # MODE 2: Process reference once + multiple angle files (efficient)
    # Uncomment the line below:
    # process_multiple_angles()
    
    
    # MODE 3: Verify reference detection first (recommended for first run)
    #verify_reference_only()
    
    
    print(" Script complete!")
   # print("   - verify_reference_only() → Check step detection")
    #print("   - main() → Process one angle file")
    #print("   - process_multiple_angles() → Batch process all angles\n")
