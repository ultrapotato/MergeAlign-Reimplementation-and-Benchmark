import subprocess
from pathlib import Path
import time

def run_mergealign(alignments_dir, output_file):
    """Run MergeAlign on the MAFFT outputs"""
    if not Path(alignments_dir).exists():
        raise ValueError(f"Alignments directory not found: {alignments_dir}")
        
    cmd = f"python3 mergealign.py -a {alignments_dir} -f {output_file}"
    try:
        result = subprocess.run(cmd, shell=True, check=True, 
                              capture_output=True, text=True)
        print(result.stdout)
        print(f"MergeAlign completed successfully")
        print(f"Output saved to: {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error running MergeAlign: {e}")
        if e.stdout:
            print("stdout:", e.stdout)
        if e.stderr:
            print("stderr:", e.stderr)

def check_setup():
    """Check if all required files and directories exist"""
    required_files = {
        'mergealign.py': 'MergeAlign implementation file',
        'mafft_alignments': 'Directory containing MAFFT alignments'
    }
    
    missing = []
    for file, description in required_files.items():
        if not Path(file).exists():
            missing.append(f"{description} ({file})")
    
    if missing:
        print("Missing required files/directories:")
        for item in missing:
            print(f"- {item}")
        return False
    return True

if __name__ == "__main__":
    start_time = time.time()
    ALIGNMENTS_DIR = "mafft_alignments"        # Directory with MAFFT alignments
    OUTPUT_FILE = "mergealign_output.fasta2"    # Where to save final alignment
    
    print("Checking setup...")
    if not check_setup():
        print("Please ensure all required files are present before running.")
        exit(1)
    
    print("Running MergeAlign...")
    run_mergealign(ALIGNMENTS_DIR, OUTPUT_FILE)
    print("Done!")
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(elapsed_time)