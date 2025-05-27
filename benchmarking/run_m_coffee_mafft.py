import os
import subprocess
import argparse

def run_tcoffee(input_file, output_file):
    command = [
        "t_coffee", input_file,
        "-method","mafft_msa, t_coffee_msa",
        "-mode", "mcoffee",  
        "-outfile", output_file
    ]
 
    try:
        subprocess.run(command, check=True)
        print(f"Alignment for {input_file} completed. Output saved to {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while processing {input_file}: {e}")

# Main function to process all fasta files in the input directory
def main(input_file, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Run T-Coffee for the provided input file
    output_file = os.path.join(output_dir, f"{os.path.splitext(os.path.basename(input_file))[0]}_aligned.fasta")
    run_tcoffee(input_file, output_file)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run T-Coffee alignment with M-Coffee mode")
    parser.add_argument("input_file", help="Path to the input fasta file")
    parser.add_argument("output_dir", help="Path to the input fasta file")

    args = parser.parse_args()

    main(args.input_file, args.output_dir)
