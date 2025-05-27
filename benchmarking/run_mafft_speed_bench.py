import os
import sys
import subprocess
from pathlib import Path

def select_test_case(run_rv = "True", input_fasta=None):
    """List and select test cases from RV100 folder"""
    test_cases = []

    if run_rv == "True":
      path = Path("../RV100")
      for file in path.glob("*.tfa"):
        test_cases.append(file)
    else:
      path = Path("../bench1.0/bali3/in")
      for file in path.glob("*"):
        test_cases.append(file)
    
    if input_fasta:
        return test_cases[int(input_fasta)-1]
    
    print("\nAvailable test cases:")
    for i, case in enumerate(test_cases):
        print(f"{i+1}. {case.name}")
    
    while True:
        try:
            choice = int(input("\nEnter the number of the test case you want to use: "))
            if 1 <= choice <= len(test_cases):
                selected_file = test_cases[choice-1]
                print(f"\nSelected test file: {selected_file}")
                return str(selected_file.absolute())
        except ValueError:
            print("Please enter a valid number!")

def run_mafft_alignments(input_fasta, matrices_dir, output_dir):
    """Run MAFFT for each matrix"""
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(exist_ok=True)
    
    # For each matrix file
    for matrix_file in os.listdir(matrices_dir):
        print(f"Processing matrix: {matrix_file}")
        matrix_path = os.path.join(matrices_dir, matrix_file)
        output_path = os.path.join(output_dir, f"{matrix_file}.aln")
        
        # Run MAFFT with this matrix
        # Note the changed --aamatrix option and added --auto for better accuracy
        cmd = f"mafft --quiet --retree 2 --amino --aamatrix {matrix_path} {input_fasta} > {output_path}"
        try:
            subprocess.run(cmd, shell=True, check=True)
            print(f"✓ Completed alignment with matrix {matrix_file}")
        except subprocess.CalledProcessError as e:
            print(f"✗ Error running MAFFT with matrix {matrix_file}: {e}")

if __name__ == "__main__":
    # Set your paths here
    input_fasta = None
    if len(sys.argv) > 1:
        input_fasta = sys.argv[1]
        OUTPUT_DIR = sys.argv[2]
        run_rv = sys.argv[3]
    
    
    INPUT_FASTA = select_test_case(run_rv, input_fasta)
    MATRICES_DIR = "../mergealign_matrices"   # Directory containing the 91 matrices
    if OUTPUT_DIR is None:
        OUTPUT_DIR = "mafft_alignments"        # Where to save MAFFT outputs
    
    print(f"\nWill use:")
    print(f"Input sequences: {INPUT_FASTA}")
    print(f"Matrices directory: {MATRICES_DIR}")
    print(f"Output directory: {OUTPUT_DIR}")
    
    if (input_fasta):
        proceed = 'y'
    else:
        proceed = input("\nProceed with MAFFT alignments? (y/n): ")
    if proceed.lower() == 'y':
        print("\nRunning MAFFT alignments...")
        run_mafft_alignments(INPUT_FASTA, MATRICES_DIR, OUTPUT_DIR)
        print("\nDone! Alignments are saved in:", OUTPUT_DIR)
        print("\nYou can now run MergeAlign on these alignments using:")
        print(f"python3 template.py -a {OUTPUT_DIR} -f final_alignment.fasta")
    else:
        print("Aborted!")