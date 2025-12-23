import os

def count_dcm_files(root_dir):
    total_count = 0
    print(f"Scanning for .dcm files in: {root_dir}")
    for dirpath, dirnames, filenames in os.walk(root_dir):
        dcm_files = [f for f in filenames if f.lower().endswith('.dcm')]
        count = len(dcm_files)
        if count > 0:
            print(f"{dirpath}: {count} .dcm files")
        total_count += count
    print(f"Total .dcm files found: {total_count}")
    return total_count

if __name__ == "__main__":
    # Example usage: update the path as needed
    # NOTE: This was one of the early utility scripts created for the project.
    # It provides a simple way to count DICOM files across directory trees,
    # useful for understanding dataset sizes before processing.
    
    # Windows network path example (original):
    network_share = r"\\mfad.mfroot.org\rchapp\Digpath\Drop\TEST-IMAGES\LeicaGT450DICOM\PowerToolsTest"
    # For macOS/Linux, use: network_share = '/path/to/dicom/files'
    # Recommended for this project: network_share = './dicom_samples'
    
    count_dcm_files(network_share)

