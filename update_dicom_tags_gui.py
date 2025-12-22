#!/usr/bin/env python3
"""
GUI version of DICOM Tag Updater for Windows executable.

This version provides a graphical interface for selecting files/folders
and configuring tag values before updating DICOM files.
"""

import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
import threading
import sys
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from pydicom import dcmread
from pydicom.uid import generate_uid
from pydicom.errors import InvalidDicomError

# Handle imports for both development and PyInstaller executable
# PyInstaller creates a temporary folder and stores path in _MEIPASS
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    base_path = Path(sys._MEIPASS)
else:
    # Running as script
    base_path = Path(__file__).parent.absolute()

# Add to path for importing dcmutl
if str(base_path) not in sys.path:
    sys.path.insert(0, str(base_path))

try:
    from dcmutl import get_dcm_files
except ImportError as e:
    # Try to show error, but if GUI isn't ready, print to console
    try:
        import tkinter.messagebox
        tkinter.messagebox.showerror("Import Error", 
            f"Could not import dcmutl module: {e}\n\n"
            f"Base path: {base_path}\n"
            f"Python path: {sys.path[:3]}")
    except:
        print(f"ERROR: Could not import dcmutl module: {e}")
        print(f"Base path: {base_path}")
    sys.exit(1)


def generate_accession_number() -> str:
    """Generate a unique accession number based on current timestamp."""
    now = datetime.now()
    microseconds = now.microsecond
    return f"{now.strftime('%Y%m%d-%H%M%S')}-{microseconds:06d}"


def is_valid_uid(uid: str) -> bool:
    """Validate that a UID follows DICOM format requirements."""
    if not uid or not isinstance(uid, str):
        return False
    if len(uid) > 64:
        return False
    components = uid.split('.')
    if not components:
        return False
    for component in components:
        if not component:
            return False
        if not component.isdigit():
            return False
        if len(component) > 1 and component.startswith('0'):
            return False
    return True


def update_tag_recursively(ds, tag_tuple: Tuple, value, vr: str = None) -> int:
    """
    Recursively update a tag in the dataset and all nested sequences.
    
    Args:
        ds: pydicom Dataset object
        tag_tuple: Tuple of (group, element) for the tag, e.g. (0x0010, 0x0010)
        value: Value to set for the tag
        vr: Value Representation (e.g., 'PN', 'LO', 'DA') - required if adding new tag
        
    Returns:
        Count of how many times the tag was updated
    """
    count = 0
    
    # Update at current level if tag exists
    if tag_tuple in ds:
        ds[tag_tuple].value = value
        count += 1
    
    # Recursively search through all sequences
    for elem in ds:
        if elem.VR == "SQ" and elem.value:
            # This is a sequence - iterate through its items
            for seq_item in elem.value:
                count += update_tag_recursively(seq_item, tag_tuple, value, vr)
    
    return count


def get_original_values(ds) -> Dict[str, Optional[str]]:
    """Extract original values from DICOM dataset."""
    originals = {
        'StudyInstanceUID': None,
        'AccessionNumber': None,
        'SeriesInstanceUID': None
    }
    try:
        if (0x0020, 0x000d) in ds:
            originals['StudyInstanceUID'] = str(ds[0x0020, 0x000d].value)
    except (AttributeError, KeyError):
        pass
    try:
        if (0x0008, 0x0050) in ds:
            originals['AccessionNumber'] = str(ds[0x0008, 0x0050].value)
    except (AttributeError, KeyError):
        pass
    try:
        if (0x0020, 0x000e) in ds:
            originals['SeriesInstanceUID'] = str(ds[0x0020, 0x000e].value)
    except (AttributeError, KeyError):
        pass
    return originals


def update_dicom_file(
    file_path: str,
    tag_values: Dict[str, str],
    progress_callback=None
) -> Tuple[bool, str]:
    """
    Update DICOM tags in a single file.
    
    Args:
        file_path: Path to DICOM file
        tag_values: Dictionary with tag values to set
        progress_callback: Optional callback function for progress updates
        
    Returns:
        Tuple of (success, message)
    """
    try:
        if progress_callback:
            progress_callback(f"Reading: {os.path.basename(file_path)}")
        
        ds = dcmread(file_path)
        original_values = get_original_values(ds)
        
        # Generate unique values
        new_study_uid = generate_uid()
        new_accession_number = generate_accession_number()
        new_series_uid = generate_uid()
        
        if progress_callback:
            progress_callback(f"Updating tags: {os.path.basename(file_path)}")
        
        # Update unique identifier tags (at root level first, then recursively in sequences)
        if (0x0020, 0x000d) not in ds:
            ds.add_new((0x0020, 0x000d), 'UI', new_study_uid)
        update_tag_recursively(ds, (0x0020, 0x000d), new_study_uid, 'UI')
        
        if (0x0008, 0x0050) not in ds:
            ds.add_new((0x0008, 0x0050), 'SH', new_accession_number)
        update_tag_recursively(ds, (0x0008, 0x0050), new_accession_number, 'SH')
        
        if (0x0020, 0x000e) not in ds:
            ds.add_new((0x0020, 0x000e), 'UI', new_series_uid)
        update_tag_recursively(ds, (0x0020, 0x000e), new_series_uid, 'UI')
        
        # Update test data tags using recursive update (updates in sequences too)
        # PatientID - (0010,0020)
        patient_id_value = tag_values.get('PatientID', '11043207')
        if (0x0010, 0x0020) not in ds:
            ds.add_new((0x0010, 0x0020), 'LO', patient_id_value)
        update_tag_recursively(ds, (0x0010, 0x0020), patient_id_value, 'LO')
        
        # PatientName - (0010,0010)
        patient_name_value = tag_values.get('PatientName', 'ZZTESTPATIENT^MIDIA THREE')
        if (0x0010, 0x0010) not in ds:
            ds.add_new((0x0010, 0x0010), 'PN', patient_name_value)
        update_tag_recursively(ds, (0x0010, 0x0010), patient_name_value, 'PN')
        
        # PatientBirthDate - (0010,0030)
        birth_date_value = tag_values.get('PatientBirthDate', '19010101')
        if (0x0010, 0x0030) not in ds:
            ds.add_new((0x0010, 0x0030), 'DA', birth_date_value)
        update_tag_recursively(ds, (0x0010, 0x0030), birth_date_value, 'DA')
        
        # InstitutionName - (0008,0080)
        institution_value = tag_values.get('InstitutionName', 'TEST FACILITY')
        if (0x0008, 0x0080) not in ds:
            ds.add_new((0x0008, 0x0080), 'LO', institution_value)
        update_tag_recursively(ds, (0x0008, 0x0080), institution_value, 'LO')
        
        # ReferringPhysicianName - (0008,0090)
        referring_physician_value = tag_values.get('ReferringPhysicianName', 'TEST PROVIDER')
        if (0x0008, 0x0090) not in ds:
            ds.add_new((0x0008, 0x0090), 'PN', referring_physician_value)
        update_tag_recursively(ds, (0x0008, 0x0090), referring_physician_value, 'PN')
        
        # Save the file
        ds.save_as(file_path, write_like_original=False)
        
        return True, "Success"
        
    except InvalidDicomError as e:
        return False, f"Invalid DICOM file: {e}"
    except Exception as e:
        return False, f"Error: {e}"


class DICOMTagUpdaterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("DICOM Tag Updater")
        self.root.geometry("800x700")
        
        # Variables
        self.path_var = tk.StringVar()
        self.processing = False
        
        # Default tag values (preselected)
        self.tag_vars = {
            'PatientID': tk.StringVar(value="11043207"),
            'PatientName': tk.StringVar(value="ZZTESTPATIENT^MIDIA THREE"),
            'PatientBirthDate': tk.StringVar(value="19010101"),
            'InstitutionName': tk.StringVar(value="TEST FACILITY"),
            'ReferringPhysicianName': tk.StringVar(value="TEST PROVIDER")
        }
        
        self.create_widgets()
    
    def create_widgets(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="DICOM Tag Updater", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Path selection
        path_frame = ttk.LabelFrame(main_frame, text="Select DICOM File or Folder", padding="10")
        path_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        path_frame.columnconfigure(1, weight=1)
        
        ttk.Label(path_frame, text="Path:").grid(row=0, column=0, padx=(0, 5), sticky=tk.W)
        path_entry = ttk.Entry(path_frame, textvariable=self.path_var, width=50)
        path_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        
        ttk.Button(path_frame, text="Browse File...", command=self.browse_file).grid(row=0, column=2, padx=(0, 5))
        ttk.Button(path_frame, text="Browse Folder...", command=self.browse_folder).grid(row=0, column=3)
        
        # Tag values configuration
        tags_frame = ttk.LabelFrame(main_frame, text="Tag Values (Editable)", padding="10")
        tags_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        tags_frame.columnconfigure(1, weight=1)
        
        row = 0
        tag_labels = {
            'PatientID': 'Patient ID (0010,0020):',
            'PatientName': 'Patient Name (0010,0010):',
            'PatientBirthDate': 'Patient Birth Date (0010,0030):',
            'InstitutionName': 'Institution Name (0008,0080):',
            'ReferringPhysicianName': 'Referring Physician Name (0008,0090):'
        }
        
        for tag_key, tag_label in tag_labels.items():
            ttk.Label(tags_frame, text=tag_label).grid(row=row, column=0, padx=(0, 10), pady=5, sticky=tk.W)
            entry = ttk.Entry(tags_frame, textvariable=self.tag_vars[tag_key], width=40)
            entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
            row += 1
        
        # Info label
        info_label = ttk.Label(main_frame, 
                              text="Note: StudyInstanceUID, AccessionNumber, and SeriesInstanceUID\nwill be automatically generated with unique timestamp-based values.",
                              font=("Arial", 9), foreground="gray")
        info_label.grid(row=3, column=0, columnspan=3, pady=(0, 10))
        
        # Process button
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=3, pady=(0, 10))
        
        self.process_btn = ttk.Button(button_frame, text="Process DICOM Files", 
                                      command=self.process_files, width=30)
        self.process_btn.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="Reset to Defaults", 
                  command=self.reset_defaults, width=20).pack(side=tk.LEFT, padx=5)
        
        # Progress bar
        self.progress_var = tk.StringVar(value="Ready")
        progress_label = ttk.Label(main_frame, textvariable=self.progress_var)
        progress_label.grid(row=5, column=0, columnspan=3, pady=(0, 5))
        
        self.progress_bar = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress_bar.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Output area
        output_frame = ttk.LabelFrame(main_frame, text="Output", padding="10")
        output_frame.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(7, weight=1)
        
        self.output_text = scrolledtext.ScrolledText(output_frame, height=15, wrap=tk.WORD)
        self.output_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Redirect stdout to text widget
        self.redirect_output()
    
    def redirect_output(self):
        """Redirect stdout to the text widget."""
        class TextRedirect:
            def __init__(self, text_widget):
                self.text_widget = text_widget
            
            def write(self, text):
                self.text_widget.insert(tk.END, text)
                self.text_widget.see(tk.END)
                self.text_widget.update_idletasks()
            
            def flush(self):
                pass
        
        sys.stdout = TextRedirect(self.output_text)
    
    def browse_file(self):
        """Browse for a single DICOM file."""
        file_path = filedialog.askopenfilename(
            title="Select DICOM File",
            filetypes=[("DICOM files", "*.dcm *.dicom"), ("All files", "*.*")]
        )
        if file_path:
            self.path_var.set(file_path)
    
    def browse_folder(self):
        """Browse for a folder containing DICOM files."""
        folder_path = filedialog.askdirectory(title="Select Folder Containing DICOM Files")
        if folder_path:
            self.path_var.set(folder_path)
    
    def reset_defaults(self):
        """Reset tag values to defaults."""
        self.tag_vars['PatientID'].set("11043207")
        self.tag_vars['PatientName'].set("ZZTESTPATIENT^MIDIA THREE")
        self.tag_vars['PatientBirthDate'].set("19010101")
        self.tag_vars['InstitutionName'].set("TEST FACILITY")
        self.tag_vars['ReferringPhysicianName'].set("TEST PROVIDER")
        messagebox.showinfo("Defaults Reset", "Tag values have been reset to defaults.")
    
    def process_files(self):
        """Process DICOM files."""
        if self.processing:
            messagebox.showwarning("Processing", "Already processing files. Please wait.")
            return
        
        path = self.path_var.get().strip()
        if not path:
            messagebox.showerror("Error", "Please select a DICOM file or folder.")
            return
        
        if not os.path.exists(path):
            messagebox.showerror("Error", f"Path does not exist: {path}")
            return
        
        # Get tag values
        tag_values = {key: var.get() for key, var in self.tag_vars.items()}
        
        # Disable button during processing
        self.process_btn.config(state=tk.DISABLED, text="Processing...")
        self.processing = True
        self.output_text.delete(1.0, tk.END)
        self.progress_bar.start()
        
        # Run in separate thread
        thread = threading.Thread(target=self._process_files_thread, args=(path, tag_values))
        thread.daemon = True
        thread.start()
    
    def _process_files_thread(self, path: str, tag_values: Dict[str, str]):
        """Process files in a separate thread."""
        try:
            stats = {'total': 0, 'success': 0, 'failed': 0}
            
            # Determine if path is file or folder
            if os.path.isfile(path):
                dcm_files = [path]
            else:
                dcm_files = get_dcm_files(path)
            
            if not dcm_files:
                self.root.after(0, lambda: messagebox.showwarning("No Files", 
                    f"No DICOM files found in: {path}"))
                self.root.after(0, self._reset_button)
                return
            
            stats['total'] = len(dcm_files)
            
            self.root.after(0, lambda: self.progress_var.set(f"Processing {stats['total']} file(s)..."))
            print(f"Found {stats['total']} DICOM file(s) to process\n")
            print("=" * 60)
            
            for idx, dcm_file in enumerate(dcm_files, 1):
                file_name = os.path.basename(dcm_file)
                self.root.after(0, lambda f=file_name, i=idx, t=stats['total']: 
                    self.progress_var.set(f"Processing [{i}/{t}]: {f}"))
                
                print(f"\n[{idx}/{stats['total']}] Processing: {file_name}")
                
                def progress_callback(msg):
                    self.root.after(0, lambda m=msg: self.progress_var.set(m))
                    print(f"  {msg}")
                
                success, message = update_dicom_file(dcm_file, tag_values, progress_callback)
                
                if success:
                    stats['success'] += 1
                    print(f"  ✓ Successfully updated")
                else:
                    stats['failed'] += 1
                    print(f"  ❌ Error: {message}")
            
            # Show completion
            print("\n" + "=" * 60)
            print("SUMMARY")
            print("=" * 60)
            print(f"Total files processed: {stats['total']}")
            print(f"Successfully updated: {stats['success']}")
            print(f"Failed: {stats['failed']}")
            print("=" * 60)
            
            self.root.after(0, lambda: self._processing_complete(stats))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"An error occurred: {str(e)}"))
            self.root.after(0, self._reset_button)
    
    def _processing_complete(self, stats: Dict[str, int]):
        """Handle processing completion."""
        message = f"Processing complete!\n\n"
        message += f"Total files: {stats['total']}\n"
        message += f"Successfully updated: {stats['success']}\n"
        message += f"Failed: {stats['failed']}\n"
        
        if stats['failed'] == 0:
            messagebox.showinfo("Complete", message)
        else:
            messagebox.showwarning("Complete with Errors", message)
        
        self._reset_button()
    
    def _reset_button(self):
        """Reset the process button."""
        self.process_btn.config(state=tk.NORMAL, text="Process DICOM Files")
        self.processing = False
        self.progress_bar.stop()
        self.progress_var.set("Ready")


if __name__ == "__main__":
    root = tk.Tk()
    app = DICOMTagUpdaterGUI(root)
    root.mainloop()

