# MergeAlign

A tool for improving multiple sequence alignment performance through consensus alignment generation.

## Installation

1. Clone this repository:
```bash
git clone https://github.com/ultrapotato/MergeAlign-Reimplementation-and-Benchmark
cd mergealign
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install MAFFT if not already installed:
```bash
# Ubuntu/Debian
sudo apt-get install mafft

# MacOS
brew install mafft
```
## Usage Pipeline

1. **Benchmark and Select Matrices**:
```bash
python benchmark_substitutionmatrices.py
```
Tests different substitution matrices on benchmark alignments to find the best performing ones. 
NOTE: This step will take a long time even though we reduced the number of benchmark MSAs for faster runtime on personal computers.
- Creates `benchmark_results_[timestamp]/` containing:
  - `matrix_rankings.txt`: Ranked list of matrices by performance
  - `detailed_results.json`: Detailed scoring data
  - `benchmark_msas.txt`: List of MSAs used in benchmarking
- Selected matrices are saved to `mergealign_matrices/`

2. **Generate MAFFT Alignments**:
```bash
python run_mafft.py
```
NOTE: We have included pre-computed MAFFT alignments in the `mafft_alignments/` directory. Running this script will take a really long time and will overwrite these pre-computed alignments. You can skip this step and use the pre-computed alignments if you wish to save time (these matrices are precomputed for testcase 75).

If you choose to run it:
- When prompted, select test case 75 (BBA0001.tfa) as it is the shortest sequence and will run the fastest for demo purposes
- Creates `mafft_alignments/` directory
- Generates one alignment file per matrix

3. **Run MergeAlign**:
```bash
python run_mergealign.py
```
Combines all individual alignments into a consensus alignment.
- Outputs final consensus alignment to `mergealign_output.fasta`
- Includes column-wise confidence scores

## Benchmarking
The benchmarking folder contains the following:
- `mergealign_matrices_true/` – folder containing substitution matrices for MergeAlign
- `bali_in/` – folder containing input sequences from Balibase v3
- `bali_ref/` – folder containing benchmark alignments from Balibase v3
- `MergeAlign.py` – our implementation of MergeAlign
- `bench_mafft.py` – runs MergeAlign pre-processing on bali_in and gathers speed data
- `bench_mergealign.py` – runs MergeAlign post-processing on MAFFT alignments and gathers speed data
- `bench_muscle.py` – runs MUSCLE on bali_in and gathers speed data
- `benchmark_acc.py` – calculate F-scores for a directory of alignments compared to benchmark alignments in bali_ref
- `benchmark_speed.py` - Runs M-Coffee and BioAlign on RV100 or bali_in
- `merge_alignments` – alignments of bali_in created through MergeAlign
- `muscle_alignments` – alignments of bali_in created through MUSCLE

The `mafft_alignments/` folder is excluded for being too large (nearly 1GB).
Other files are helper files.

### Reproducing Benchmarking

To reproduce MergeAlign pre-processing speed benchmarking, run `python bench_mafft.py`. This will produce alignments in a folder called `mafft_alignments/`, and speed data in `mafft_speed.xlsx`.

To reproduce MergeAlign post-processing speed benchmarking, run `python bench_mergealign.py`. This uses the `mafft_alignments/` folder to produce alignments in `merge_alignments/` and speed data in `merge_speed.xlsx`.

To reproduce MUSCLE speed benchmarking, change the path to the MUSCLE executable in bench_muscle.py (marked by a NOTE in the code) to the correct path, then run `python bench_muscle.py`. This produces alignments in `muscle_alignments/` and logs speed data in `muscle_speed.xlsx`.

MUSCLE can be downloaded from https://drive5.com/muscle/.

Tp reproduce BioAlign and M-Coffee speed benchmarking, run `python benchmark_speed.py`. This uses and modifies the `mafft_alignments/` folder and produces alignments in `bioalign_output/` and `m_coffee_out/`. The speed data is located in `speed_benchmark_results.csv`. Running it with no arguments takes in sequences from the `RV100` folder, and entering bali_in uses the sequences in `bali_in`.

T-Coffee can be downloaded from http://tcoffee-packages.s3-website.eu-central-1.amazonaws.com/#Stable/Latest/.

To reproduce accuracy benchmarking, run `python benchmark_acc.py <benchmark_directory> <inferred directory> <MSA method>`. The benchmark directory can be `bali_ref/`, the inferred directory can be either `merge_alignemnts/` or `muscle_alignments/`, and the MSA method can be `merge` or `muscle`. For instance, `python benchmark_acc.py bali_ref muscle_alignments muscle`.

### Benchmarking Results
Benchmarking results can be found in the `benchmark_final_results/` folder.

### Benchmarking Analysis
R code for benchmark analysis can be found in the `Merge_R/` folder.

## Note
Ensure all files are in the root directory before running scripts.

