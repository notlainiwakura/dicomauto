#!/usr/bin/env python3
"""
Standalone script to update DICOM tags in all files within a specified folder.

This script processes DICOM files and updates critical tags with unique timestamp-based
values, including StudyInstanceUID, AccessionNumber, and SeriesInstanceUID. It also
updates other test tags as specified and verifies all changes are valid.

Usage:
    python update_dicom_tags.py <folder_path> [--verbose] [--dry-run]
"""

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Tuple
from pydicom import dcmread
from pydicom.uid import generate_uid
from pydicom.errors import InvalidDicomError

# Add project root to path to allow importing dcmutl
script_dir = Path(__file__).parent.absolute()
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from dcmutl import get_dcm_files, update_tags_ds
except ImportError as e:
    print(f"Error: Could not import dcmutl module: {e}", file=sys.stderr)
    print("Make sure you're running this script from the project root directory.", file=sys.stderr)
    sys.exit(1)


def generate_accession_number() -> str:
    """
    Generate a unique accession number based on current timestamp.
    
    Returns:
        Accession number in format: YYYYMMDD-HHMMSS-{microseconds}
    """
    now = datetime.now()
    microseconds = now.microsecond
    return f"{now.strftime('%Y%m%d-%H%M%S')}-{microseconds:06d}"


def is_valid_uid(uid: str) -> bool:
    """
    Validate that a UID follows DICOM format requirements.
    
    DICOM UIDs must:
    - Contain only numeric characters and dots
    - Each component must not start with 0 (unless it's a single 0)
    - Maximum length of 64 characters
    - Components separated by dots
    
    Args:
        uid: UID string to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not uid or not isinstance(uid, str):
        return False
    
    if len(uid) > 64:
        return False
    
    # Split by dots and validate each component
    components = uid.split('.')
    if not components:
        return False
    
    for component in components:
        if not component:
            return False
        # Component must be numeric
        if not component.isdigit():
            return False
        # Component must not start with 0 unless it's just "0"
        if len(component) > 1 and component.startswith('0'):
            return False
    
    return True


def get_original_values(ds) -> Dict[str, Optional[str]]:
    """
    Extract original values from DICOM dataset.
    
    Args:
        ds: pydicom Dataset object
        
    Returns:
        Dictionary with original values for StudyInstanceUID, AccessionNumber, SeriesInstanceUID
    """
    originals = {
        'StudyInstanceUID': None,
        'AccessionNumber': None,
        'SeriesInstanceUID': None
    }
    
    try:
        if hasattr(ds, 'StudyInstanceUID'):
            originals['StudyInstanceUID'] = str(ds.StudyInstanceUID)
    except (AttributeError, KeyError):
        pass
    
    try:
        if hasattr(ds, 'AccessionNumber'):
            originals['AccessionNumber'] = str(ds.AccessionNumber)
    except (AttributeError, KeyError):
        pass
    
    try:
        if hasattr(ds, 'SeriesInstanceUID'):
            originals['SeriesInstanceUID'] = str(ds.SeriesInstanceUID)
    except (AttributeError, KeyError):
        pass
    
    return originals


def update_dicom_file(
    file_path: str,
    dry_run: bool = False,
    verbose: bool = False
) -> Tuple[bool, str, Dict[str, Optional[str]], Dict[str, Optional[str]]]:
    """
    Update DICOM tags in a single file.
    
    Args:
        file_path: Path to DICOM file
        dry_run: If True, don't actually modify the file
        verbose: If True, print detailed information
        
    Returns:
        Tuple of (success, message, original_values, new_values)
    """
    try:
        # Read DICOM file
        print("  Step 0: Reading DICOM file...")
        ds = dcmread(file_path)
        print("    ✓ File read successfully")
        
        # Get original values (stored but not displayed for security)
        original_values = get_original_values(ds)
        
        # Generate unique values
        print("  Step 1: Generating unique timestamp-based values...")
        new_study_uid = generate_uid()
        new_accession_number = generate_accession_number()
        new_series_uid = generate_uid()
        
        new_values = {
            'StudyInstanceUID': new_study_uid,
            'AccessionNumber': new_accession_number,
            'SeriesInstanceUID': new_series_uid
        }
        
        # Log new values (security: only show new values, not originals)
        print("  Step 2: Updating tags with new values:")
        print(f"    → StudyInstanceUID: {new_study_uid}")
        print(f"    → AccessionNumber: {new_accession_number}")
        print(f"    → SeriesInstanceUID: {new_series_uid}")
        
        if verbose:
            print(f"  [Verbose] Original StudyInstanceUID: {original_values['StudyInstanceUID']}")
            print(f"  [Verbose] Original AccessionNumber: {original_values['AccessionNumber']}")
            print(f"  [Verbose] Original SeriesInstanceUID: {original_values['SeriesInstanceUID']}")
        
        if not dry_run:
            # Update unique tags
            print("  Step 3: Updating unique identifier tags...")
            update_tags_ds(ds, "StudyInstanceUID", new_study_uid)
            update_tags_ds(ds, "AccessionNumber", new_accession_number)
            update_tags_ds(ds, "SeriesInstanceUID", new_series_uid)
            print("    ✓ Unique identifier tags updated")
            
            # Update other test tags
            print("  Step 4: Updating test data tags...")
            update_tags_ds(ds, "PatientID", "11043207")
            print("    ✓ PatientID updated")
            update_tags_ds(ds, "PatientName", "ZZTESTPATIENT^MIDIA THREE")
            print("    ✓ PatientName updated")
            update_tags_ds(ds, "PatientBirthDate", "19010101")
            print("    ✓ PatientBirthDate updated")
            update_tags_ds(ds, "InstitutionName", "TEST FACILITY")
            print("    ✓ InstitutionName updated")
            
            # Try ReferringPhysicianName tag (0008,0090) first, fallback to (0808,0090)
            referring_physician_set = False
            try:
                if hasattr(ds, 'ReferringPhysicianName'):
                    update_tags_ds(ds, "ReferringPhysicianName", "TEST PROVIDER")
                    referring_physician_set = True
                    print("    ✓ ReferringPhysicianName updated (standard tag)")
                else:
                    # Try to add the standard tag if it doesn't exist
                    try:
                        if (0x0008, 0x0090) not in ds:
                            ds.add_new((0x0008, 0x0090), 'PN', "TEST PROVIDER")
                        else:
                            ds[0x0008, 0x0090].value = "TEST PROVIDER"
                        referring_physician_set = True
                        print("    ✓ ReferringPhysicianName updated (standard tag added)")
                    except Exception:
                        pass
            except (AttributeError, KeyError, Exception):
                pass
            
            if not referring_physician_set:
                # Try private tag (0808,0090)
                try:
                    if (0x0808, 0x0090) in ds:
                        ds[0x0808, 0x0090].value = "TEST PROVIDER"
                        referring_physician_set = True
                        print("    ✓ ReferringPhysicianName updated (private tag)")
                    else:
                        # Add the tag if it doesn't exist
                        ds.add_new((0x0808, 0x0090), 'PN', "TEST PROVIDER")
                        referring_physician_set = True
                        print("    ✓ ReferringPhysicianName updated (private tag added)")
                except Exception as e:
                    print(f"    ⚠ Warning: Could not set ReferringPhysicianName: {e}")
            
            # Save the file
            print("  Step 5: Saving updated DICOM file...")
            ds.save_as(file_path, write_like_original=False)
            print("    ✓ File saved successfully")
        
        return True, "Success", original_values, new_values
        
    except InvalidDicomError as e:
        return False, f"Invalid DICOM file: {e}", {}, {}
    except Exception as e:
        return False, f"Error processing file: {e}", {}, {}


def verify_changes(
    file_path: str,
    original_values: Dict[str, Optional[str]],
    new_values: Dict[str, Optional[str]]
) -> Tuple[bool, str]:
    """
    Verify that the changes were applied correctly and values are valid.
    
    Args:
        file_path: Path to DICOM file
        original_values: Dictionary of original values
        new_values: Dictionary of new values
        
    Returns:
        Tuple of (success, message)
    """
    try:
        # Re-read the file
        ds = dcmread(file_path)
        
        verification_errors = []
        
        # Verify StudyInstanceUID
        print("    → Verifying StudyInstanceUID...")
        if hasattr(ds, 'StudyInstanceUID'):
            current_uid = str(ds.StudyInstanceUID)
            if current_uid == original_values.get('StudyInstanceUID'):
                verification_errors.append("StudyInstanceUID did not change")
            elif not is_valid_uid(current_uid):
                verification_errors.append(f"StudyInstanceUID is not valid: {current_uid}")
            elif current_uid != new_values.get('StudyInstanceUID'):
                verification_errors.append(f"StudyInstanceUID mismatch: expected {new_values.get('StudyInstanceUID')}, got {current_uid}")
            else:
                print("      ✓ StudyInstanceUID verified")
        else:
            verification_errors.append("StudyInstanceUID tag missing after update")
        
        # Verify AccessionNumber
        print("    → Verifying AccessionNumber...")
        if hasattr(ds, 'AccessionNumber'):
            current_acc = str(ds.AccessionNumber)
            if current_acc == original_values.get('AccessionNumber'):
                verification_errors.append("AccessionNumber did not change")
            elif current_acc != new_values.get('AccessionNumber'):
                verification_errors.append(f"AccessionNumber mismatch: expected {new_values.get('AccessionNumber')}, got {current_acc}")
            else:
                print(f"      ✓ AccessionNumber verified: {current_acc}")
        else:
            verification_errors.append("AccessionNumber tag missing after update")
        
        # Verify SeriesInstanceUID
        print("    → Verifying SeriesInstanceUID...")
        if hasattr(ds, 'SeriesInstanceUID'):
            current_series_uid = str(ds.SeriesInstanceUID)
            if current_series_uid == original_values.get('SeriesInstanceUID'):
                verification_errors.append("SeriesInstanceUID did not change")
            elif not is_valid_uid(current_series_uid):
                verification_errors.append(f"SeriesInstanceUID is not valid: {current_series_uid}")
            elif current_series_uid != new_values.get('SeriesInstanceUID'):
                verification_errors.append(f"SeriesInstanceUID mismatch: expected {new_values.get('SeriesInstanceUID')}, got {current_series_uid}")
            else:
                print("      ✓ SeriesInstanceUID verified")
        else:
            verification_errors.append("SeriesInstanceUID tag missing after update")
        
        if verification_errors:
            return False, "; ".join(verification_errors)
        
        return True, "All verifications passed"
        
    except Exception as e:
        return False, f"Verification error: {e}"


def process_folder(
    folder_path: str,
    dry_run: bool = False,
    verbose: bool = False
) -> Dict[str, int]:
    """
    Process all DICOM files in a folder.
    
    Args:
        folder_path: Path to folder containing DICOM files
        dry_run: If True, don't actually modify files
        verbose: If True, print detailed information
        
    Returns:
        Dictionary with statistics about processing
    """
    stats = {
        'total': 0,
        'success': 0,
        'failed': 0,
        'verification_failed': 0
    }
    
    # Normalize path for Windows (handle both forward and backslashes)
    folder_path = os.path.normpath(folder_path)
    
    # Validate folder exists
    if not os.path.exists(folder_path):
        print(f"Error: Folder does not exist: {folder_path}", file=sys.stderr)
        print(f"  Resolved path: {os.path.abspath(folder_path)}", file=sys.stderr)
        return stats
    
    if not os.path.isdir(folder_path):
        print(f"Error: Path is not a directory: {folder_path}", file=sys.stderr)
        return stats
    
    print("=" * 60)
    print("DICOM TAG UPDATER")
    print("=" * 60)
    print(f"Processing folder: {folder_path}")
    if verbose:
        print(f"Absolute path: {os.path.abspath(folder_path)}")
    print()
    
    # Get all DICOM files
    print("Searching for DICOM files...")
    dcm_files = get_dcm_files(folder_path)
    
    if not dcm_files:
        print(f"Warning: No DICOM files found in folder: {folder_path}", file=sys.stderr)
        if verbose:
            # List what files are actually in the directory
            try:
                files_in_dir = os.listdir(folder_path)
                print(f"  Files in directory: {len(files_in_dir)} items")
                if files_in_dir:
                    print(f"  Sample files: {files_in_dir[:5]}")
            except Exception as e:
                print(f"  Could not list directory contents: {e}")
        return stats
    
    stats['total'] = len(dcm_files)
    
    print("=" * 60)
    print(f"Found {stats['total']} DICOM file(s) to process")
    if dry_run:
        print("⚠ DRY RUN MODE: Files will not be modified")
    print("=" * 60)
    print()
    
    # Process each file
    for idx, dcm_file in enumerate(dcm_files, 1):
        print(f"[{idx}/{stats['total']}] Processing: {os.path.basename(dcm_file)}")
        
        if verbose:
            print(f"  Full path: {dcm_file}")
        
        success, message, original_values, new_values = update_dicom_file(
            dcm_file,
            dry_run=dry_run,
            verbose=verbose
        )
        
        if not success:
            print(f"  ❌ ERROR: {message}")
            stats['failed'] += 1
            print()
            continue
        
        stats['success'] += 1
        
        if not dry_run:
            # Verify changes
            print("  Step 6: Verifying changes...")
            verify_success, verify_message = verify_changes(
                dcm_file,
                original_values,
                new_values
            )
            
            if not verify_success:
                print(f"  ❌ VERIFICATION FAILED: {verify_message}")
                stats['verification_failed'] += 1
            else:
                print("  ✓ Verification passed: All tags updated correctly")
        else:
            print("  ℹ Skipping verification in dry-run mode")
        
        print(f"  ✓ File {idx}/{stats['total']} completed successfully")
        print()
    
    return stats


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description='Update DICOM tags in all files within a specified folder.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python update_dicom_tags.py /path/to/dicom/folder
  python update_dicom_tags.py /path/to/dicom/folder --verbose
  python update_dicom_tags.py /path/to/dicom/folder --dry-run
        """
    )
    
    parser.add_argument(
        'folder',
        type=str,
        help='Path to folder containing DICOM files'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without modifying files'
    )
    
    args = parser.parse_args()
    
    # Process the folder
    stats = process_folder(
        args.folder,
        dry_run=args.dry_run,
        verbose=args.verbose
    )
    
    # Print summary
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total files processed: {stats['total']}")
    print(f"Successfully updated: {stats['success']}")
    print(f"Failed: {stats['failed']}")
    if not args.dry_run:
        print(f"Verification failed: {stats['verification_failed']}")
    print("=" * 60)
    
    # Exit with appropriate code
    if stats['failed'] > 0 or stats['verification_failed'] > 0:
        sys.exit(1)
    elif stats['total'] == 0:
        sys.exit(2)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()

