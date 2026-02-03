# Gait-MTC-segmentation-analysis
# plt.py algorithm: Use this for exploratory analysis of one file 
	Overview: This Python script is currently analyzing gait patterns from motion capture data (C3D format) by just detecting swing phase (peak) and foot strikes (min. Point post peak) in vertical displacement trajectories. The tool automatically identifies gait events, calculating displacement metrics, and generating visualization for further biomechanical gait analysis. 
	
  Features:
Automatic Peak Detection: Identifies swing phase peaks using scipy signal processing 
Step Detection: Detects foot strikes at valley point (lowest displacement)
Data Export: Generates Excel workbook with three sheets (displacement data, peaks, steps)
Visualization: Create plots with marked gait events. 
Statistical Summary: Calculates average peak and step displacements
Combined Report: Console table showing peaks and steps. 
