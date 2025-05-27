import os
import subprocess
from pathlib import Path
import time

def select_test_case():
    """List and select test cases from RV100 folder"""
    test_cases = []
    rv100_path = Path("RV100")  
    
    for file in rv100_path.glob("*.tfa"): 
        test_cases.append(file)
    
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
    Path(output_dir).mkdir(exist_ok=True)
    
    for matrix_file in os.listdir(matrices_dir):
        print(f"Processing matrix: {matrix_file}")
        matrix_path = os.path.join(matrices_dir, matrix_file)
        output_path = os.path.join(output_dir, f"{matrix_file}.aln")
        
        cmd = f"mafft --quiet --auto --amino --aamatrix {matrix_path} {input_fasta} > {output_path}"
        try:
            subprocess.run(cmd, shell=True, check=True)
            print(f"✓ Completed alignment with matrix {matrix_file}")
        except subprocess.CalledProcessError as e:
            print(f"✗ Error running MAFFT with matrix {matrix_file}: {e}")

if __name__ == "__main__":
    print("First, select your test sequence file:")
    INPUT_FASTA = select_test_case()
    
    MATRICES_DIR = "mergealign_matrices"
    OUTPUT_DIR = "mafft_alignments"
    
    print(f"\nWill use:")
    print(f"Input sequences: {INPUT_FASTA}")
    print(f"Matrices directory: {MATRICES_DIR}")
    print(f"Output directory: {OUTPUT_DIR}")
    
    proceed = input("\nProceed with MAFFT alignments? (y/n): ")
    if proceed.lower() == 'y':
        start_time = time.time()
        print("\nRunning MAFFT alignments...")
        run_mafft_alignments(INPUT_FASTA, MATRICES_DIR, OUTPUT_DIR)
        print("\nDone! Alignments are saved in:", OUTPUT_DIR)
        print("\nYou can now run MergeAlign on these alignments using:")
        print(f"python mergealign.py -a {OUTPUT_DIR} -f mergealign_output.fasta")
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"\nTotal time: {elapsed_time:.2f} seconds")
    else:
        print("Aborted!")