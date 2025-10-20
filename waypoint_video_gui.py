#!/usr/bin/env python3
"""
Waypoint-Video Correlator GUI

A graphical user interface for the waypoint-video correlation tool.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
import csv
from pathlib import Path
from waypoint_video_correlator import WaypointVideoCorrelator


class WaypointVideoGUI:
    """Main GUI application for waypoint-video correlation."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Waypoint-Video Correlator")
        self.root.geometry("800x700")
        self.root.minsize(600, 500)
        
        # Variables
        self.gpx_file = tk.StringVar()
        self.video_directory = tk.StringVar()
        self.output_file = tk.StringVar(value="waypoint_video_correlation.csv")
        self.correlation_results = []
        
        self.setup_ui()
        self.center_window()
    
    def setup_ui(self):
        """Set up the user interface."""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Waypoint-Video Correlator", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # GPX File Selection
        ttk.Label(main_frame, text="GPX File:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.gpx_file, width=50).grid(
            row=1, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=5)
        ttk.Button(main_frame, text="Browse", 
                  command=self.browse_gpx_file).grid(row=1, column=2, pady=5)
        
        # Video Directory Selection
        ttk.Label(main_frame, text="Video Directory:").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.video_directory, width=50).grid(
            row=2, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=5)
        ttk.Button(main_frame, text="Browse", 
                  command=self.browse_video_directory).grid(row=2, column=2, pady=5)
        
        # Output File Selection
        ttk.Label(main_frame, text="Output CSV:").grid(row=3, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.output_file, width=50).grid(
            row=3, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=5)
        ttk.Button(main_frame, text="Browse", 
                  command=self.browse_output_file).grid(row=3, column=2, pady=5)
        
        # Buttons Frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=4, column=0, columnspan=3, pady=20)
        
        # Run Correlation Button
        self.run_button = ttk.Button(buttons_frame, text="Run Correlation", 
                                   command=self.run_correlation, style="Accent.TButton")
        self.run_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Clear Button
        ttk.Button(buttons_frame, text="Clear", 
                  command=self.clear_all).pack(side=tk.LEFT, padx=(0, 10))
        
        # Export Results Button
        self.export_button = ttk.Button(buttons_frame, text="Export Results", 
                                      command=self.export_results, state=tk.DISABLED)
        self.export_button.pack(side=tk.LEFT)
        
        # Progress Bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # Status Label
        self.status_label = ttk.Label(main_frame, text="Ready to correlate waypoints with videos")
        self.status_label.grid(row=6, column=0, columnspan=3, pady=5)
        
        # Results Frame
        results_frame = ttk.LabelFrame(main_frame, text="Correlation Results", padding="5")
        results_frame.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(7, weight=1)
        
        # Results Text Area
        self.results_text = scrolledtext.ScrolledText(results_frame, height=15, width=80)
        self.results_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure text tags for formatting
        self.results_text.tag_configure("header", font=("Arial", 10, "bold"))
        self.results_text.tag_configure("success", foreground="green")
        self.results_text.tag_configure("error", foreground="red")
        self.results_text.tag_configure("warning", foreground="orange")
    
    def center_window(self):
        """Center the window on the screen."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def browse_gpx_file(self):
        """Browse for GPX file."""
        filename = filedialog.askopenfilename(
            title="Select GPX File",
            filetypes=[("GPX files", "*.gpx"), ("All files", "*.*")]
        )
        if filename:
            self.gpx_file.set(filename)
    
    def browse_video_directory(self):
        """Browse for video directory."""
        directory = filedialog.askdirectory(title="Select Video Directory")
        if directory:
            self.video_directory.set(directory)
    
    def browse_output_file(self):
        """Browse for output CSV file."""
        filename = filedialog.asksaveasfilename(
            title="Save Correlation Results As",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            self.output_file.set(filename)
    
    def clear_all(self):
        """Clear all input fields and results."""
        self.gpx_file.set("")
        self.video_directory.set("")
        self.output_file.set("waypoint_video_correlation.csv")
        self.results_text.delete(1.0, tk.END)
        self.correlation_results = []
        self.export_button.config(state=tk.DISABLED)
        self.status_label.config(text="Ready to correlate waypoints with videos")
    
    def update_status(self, message, status_type="info"):
        """Update status label with message."""
        self.status_label.config(text=message)
        if status_type == "error":
            self.status_label.config(foreground="red")
        elif status_type == "success":
            self.status_label.config(foreground="green")
        else:
            self.status_label.config(foreground="black")
    
    def log_message(self, message, tag=""):
        """Add message to results text area."""
        self.results_text.insert(tk.END, message + "\n", tag)
        self.results_text.see(tk.END)
        self.root.update_idletasks()
    
    def validate_inputs(self):
        """Validate input files and directories."""
        if not self.gpx_file.get():
            messagebox.showerror("Error", "Please select a GPX file")
            return False
        
        if not os.path.exists(self.gpx_file.get()):
            messagebox.showerror("Error", "GPX file does not exist")
            return False
        
        if not self.video_directory.get():
            messagebox.showerror("Error", "Please select a video directory")
            return False
        
        if not os.path.exists(self.video_directory.get()):
            messagebox.showerror("Error", "Video directory does not exist")
            return False
        
        return True
    
    def run_correlation(self):
        """Run the correlation process in a separate thread."""
        if not self.validate_inputs():
            return
        
        # Disable run button and start progress
        self.run_button.config(state=tk.DISABLED)
        self.progress.start()
        self.results_text.delete(1.0, tk.END)
        self.export_button.config(state=tk.DISABLED)
        
        # Start correlation in separate thread
        thread = threading.Thread(target=self._correlation_worker)
        thread.daemon = True
        thread.start()
    
    def _correlation_worker(self):
        """Worker function for correlation process."""
        try:
            self.log_message("Starting correlation process...", "header")
            self.update_status("Parsing GPX file...")
            
            # Create correlator
            correlator = WaypointVideoCorrelator(
                self.gpx_file.get(), 
                self.video_directory.get()
            )
            
            # Parse GPX
            waypoints = correlator.gpx_parser.parse()
            if not waypoints:
                self.log_message("ERROR: No waypoints found in GPX file", "error")
                self._correlation_finished(False)
                return
            
            self.log_message(f"Found {len(waypoints)} waypoints", "success")
            
            # Find video files
            video_files = correlator._find_video_files()
            if not video_files:
                self.log_message("ERROR: No video files found in directory", "error")
                self._correlation_finished(False)
                return
            
            self.log_message(f"Found {len(video_files)} video files", "success")
            
            # Extract video metadata
            self.update_status("Extracting video metadata...")
            video_metadata = {}
            for i, video_file in enumerate(video_files, 1):
                self.log_message(f"Processing video {i}/{len(video_files)}: {os.path.basename(video_file)}")
                metadata = correlator.video_extractor.extract_metadata(video_file)
                video_metadata[video_file] = metadata
            
            # Correlate waypoints with videos
            self.update_status("Correlating waypoints with videos...")
            correlations = correlator._correlate_waypoints_videos(waypoints, video_metadata)
            
            # Save results
            self.update_status("Saving results...")
            correlator._write_csv(correlations, self.output_file.get())
            
            # Store results for display
            self.correlation_results = correlations
            
            # Display results
            self._display_results(correlations)
            
            self.log_message(f"\nCorrelation completed successfully!", "success")
            self.log_message(f"Results saved to: {self.output_file.get()}", "success")
            self._correlation_finished(True)
            
        except Exception as e:
            self.log_message(f"ERROR: {str(e)}", "error")
            self._correlation_finished(False)
    
    def _display_results(self, correlations):
        """Display correlation results in the text area."""
        self.log_message("\n" + "="*80, "header")
        self.log_message("CORRELATION RESULTS", "header")
        self.log_message("="*80, "header")
        
        matched_count = 0
        unmatched_count = 0
        
        for i, correlation in enumerate(correlations, 1):
            waypoint_name = correlation['waypoint_name']
            video_file = correlation['video_file']
            time_offset = correlation['time_offset_formatted']
            description = correlation['waypoint_description']
            
            if video_file == 'NO_MATCH':
                self.log_message(f"\n{i}. ❌ {waypoint_name} - NO VIDEO MATCH", "error")
                self.log_message(f"   Description: {description}")
                unmatched_count += 1
            else:
                self.log_message(f"\n{i}. ✅ {waypoint_name} → {video_file}", "success")
                self.log_message(f"   Time Offset: {time_offset}")
                self.log_message(f"   Description: {description}")
                matched_count += 1
        
        self.log_message(f"\n" + "="*80, "header")
        self.log_message(f"SUMMARY: {matched_count} matched, {unmatched_count} unmatched", "header")
        self.log_message("="*80, "header")
    
    def _correlation_finished(self, success):
        """Handle correlation completion."""
        self.progress.stop()
        self.run_button.config(state=tk.NORMAL)
        
        if success:
            self.export_button.config(state=tk.NORMAL)
            self.update_status("Correlation completed successfully!", "success")
        else:
            self.update_status("Correlation failed. Check results for details.", "error")
    
    def export_results(self):
        """Export results to a different file."""
        if not self.correlation_results:
            messagebox.showwarning("Warning", "No results to export")
            return
        
        filename = filedialog.asksaveasfilename(
            title="Export Results As",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                fieldnames = [
                    'waypoint_name', 'waypoint_lat', 'waypoint_lon', 'waypoint_timestamp',
                    'video_file', 'video_full_path', 'video_creation_time', 'video_duration',
                    'time_offset_seconds', 'time_offset_formatted', 'waypoint_description'
                ]
                
                with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(self.correlation_results)
                
                messagebox.showinfo("Success", f"Results exported to {filename}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export results: {str(e)}")


def main():
    """Main entry point for the GUI application."""
    root = tk.Tk()
    
    # Set style
    style = ttk.Style()
    style.theme_use('clam')  # Use a modern theme
    
    # Create and run the application
    app = WaypointVideoGUI(root)
    
    # Handle window closing
    def on_closing():
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()