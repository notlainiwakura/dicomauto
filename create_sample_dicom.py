"""
Script to create a sample DICOM file for testing.
Creates a minimal valid DICOM file that can be used with the test suite.
"""

import pydicom
from pydicom.dataset import FileDataset
from pydicom.uid import generate_uid
import numpy as np
from datetime import datetime
from pathlib import Path

def create_sample_dicom(output_path: Path):
    """Create a minimal valid DICOM file for testing."""
    
    # Create a minimal DICOM file
    ds = FileDataset("sample.dcm", {}, file_meta=None, preamble=b"\x00" * 128)
    
    # Add required DICOM tags
    ds.PatientName = "Test^Patient"
    ds.PatientID = "TEST001"
    ds.StudyInstanceUID = generate_uid()
    ds.SeriesInstanceUID = generate_uid()
    ds.SOPInstanceUID = generate_uid()
    ds.SOPClassUID = "1.2.840.10008.5.1.4.1.1.1"  # CR Image Storage
    ds.Modality = "CR"
    ds.StudyDate = datetime.now().strftime("%Y%m%d")
    ds.StudyTime = datetime.now().strftime("%H%M%S")
    ds.Rows = 256
    ds.Columns = 256
    ds.BitsAllocated = 16
    ds.BitsStored = 12
    ds.HighBit = 11
    ds.PixelRepresentation = 0
    ds.SamplesPerPixel = 1
    ds.PhotometricInterpretation = "MONOCHROME2"
    ds.PixelSpacing = [1.0, 1.0]
    
    # Create simple pixel data (random test pattern)
    ds.PixelData = np.random.randint(0, 4096, (256, 256), dtype=np.uint16).tobytes()
    
    # Save
    output_path.parent.mkdir(parents=True, exist_ok=True)
    ds.save_as(str(output_path), write_like_original=False)
    print(f"Created sample DICOM file: {output_path}")
    return output_path

if __name__ == "__main__":
    output_dir = Path("dicom_samples")
    output_file = output_dir / "sample.dcm"
    create_sample_dicom(output_file)
    print(f"Sample DICOM file created successfully at {output_file.absolute()}")

