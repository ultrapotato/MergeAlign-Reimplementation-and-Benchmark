import sys
import time
import psutil
import subprocess
import csv
from pathlib import Path

def run_script_and_benchmark(script_path, args, tool_name):
    """Run a script and benchmark its performance as given by: Runtime, peak memory usage."""
    if not Path(script_path).exists():
        raise ValueError(f"Script not found: {script_path}")
    
    cmd = ["python3", script_path] + args
    
    start_time = time.time()
    
    # Track memory usage over time
    peak_memory = 0
    mem_usage_before = psutil.Process().memory_info().rss  # Initial memory usage
    
    try:
        result = subprocess.run(
            cmd, 
            check=True, 
            text=True
        )
        print(f"{tool_name} completed successfully:\n{result.stdout}")
        if result.stderr:
            print(f"Error: {result.stderr}")
    except subprocess.CalledProcessError as e:
        print(f"Error running {tool_name}: {e.stderr}")
    
    end_time = time.time()
    
    runtime = end_time - start_time  # Total runtime in seconds
    
    # Monitor memory usage during execution
    mem_after = psutil.Process().memory_info().rss
    peak_memory = max(peak_memory, mem_after)  # Peak memory (RSS)
    
    # Convert memory to MB
    mem_usage_before_MB = mem_usage_before / (1024 * 1024)  
    mem_after_MB = mem_after / (1024 * 1024)
    peak_memory_MB = peak_memory / (1024 * 1024)  # Peak memory in MB? I'll come back to this
    
    return runtime, mem_usage_before_MB, mem_after_MB, peak_memory_MB

def write_to_csv(csv_file, runtime_mafft, runtime_mergealign, runtime_bioalign, runtime_mcoffee, tool_args):
    """Write the results of the benchmark to a CSV file."""
    file_exists = Path(csv_file).exists()
    
    with open(csv_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        
        if not file_exists:
            writer.writerow(['Source file','MAFFT Runtime (seconds)', 'MergeAlign Runtime (seconds)', 'BioAlign Runtime (seconds)', 'MCoffee Runtime (seconds)'])
        writer.writerow([(tool_args), f"{runtime_mafft:.2f}",f"{runtime_mergealign:.2f}",f"{runtime_bioalign:.2f}", f"{runtime_mcoffee:.2f}"])

def benchmark_tools(file, run_rv, arg=None):
    alignment_folder = 'mafft_alignments'
    mafft_script = "run_mafft_speed_bench.py"
    mafft_args = [str(arg), alignment_folder, str(run_rv)]
    mergealign_script = "run_mergealign.py"
    mergealign_args = [alignment_folder, 'mergealign_output.fasta']
    bioalign_script = "biopython_msa.py"
    bioalign_output_dir = "bioalign_output"
    bioalign_args = []#to be decided later
    mcoffee_script = "run_m_coffee_mafft.py"
    mcoffee_args = [str(file), "m_coffee_out"]
    # Output CSV file to store results
    csv_output_file = "speed_benchmark_results.csv"
    if run_rv:
        rvfile = (str(file))[9:]
    else:
        rvfile = (str(file))[24:]
    bioalign_args = [alignment_folder, bioalign_output_dir,rvfile]

    # Benchmark MAFFT
    print("Running MAFFT...")
    mafft_runtime, mafft_mem_before, mafft_mem_after, mafft_peak_memory = run_script_and_benchmark(mafft_script, mafft_args, "MAFFT")
    print(f"MAFFT: Runtime = {mafft_runtime:.2f}s, Memory Before = {mafft_mem_before:.2f}MB, Memory After = {mafft_mem_after:.2f}MB, Peak Memory = {mafft_peak_memory:.2f}MB")
    
    # Benchmark MergeAlign
    print("Running MergeAlign...")
    mergealign_runtime, mergealign_mem_before, mergealign_mem_after, mergealign_peak_memory = run_script_and_benchmark(mergealign_script, mergealign_args, "MergeAlign")
    print(f"MergeAlign: Runtime = {mergealign_runtime:.2f}s, Memory Before = {mergealign_mem_before:.2f}MB, Memory After = {mergealign_mem_after:.2f}MB, Peak Memory = {mergealign_peak_memory:.2f}MB")

    # Benchmark BIOAlign
    print("Running BioAlign...")
    bioalign_runtime, bioalign_mem_before, bioalign_mem_after, bioalign_peak_memory = run_script_and_benchmark(bioalign_script, bioalign_args, "BioAlign")
    print(f"BioAlign: Runtime = {mergealign_runtime:.2f}s, Memory Before = {bioalign_mem_before:.2f}MB, Memory After = {bioalign_mem_after:.2f}MB, Peak Memory = {bioalign_peak_memory:.2f}MB")
    print(file)

    # Benchmark M-coffee
    print("Running M-Coffee...")
    m_coffee_runtime, mem_before, mem_after, peak_memory = run_script_and_benchmark(mcoffee_script, mcoffee_args, "M-COFFEE")
    print(f"MCOFFEE: Runtime = {m_coffee_runtime:.2f}s, Memory Before = {mem_before:.2f}MB, Memory After = {mem_after:.2f}MB, Peak Memory = {peak_memory:.2f}MB")

    write_to_csv(csv_output_file, mafft_runtime, mergealign_runtime, bioalign_runtime, m_coffee_runtime, rvfile)
    
    print("Speed benchmarking complete!")


if __name__ == "__main__":
    if len(sys.argv) == 1:
        run_rv = False
    else:
        run_rv = (sys.argv[1] == "RV100")
    
    # run_rv = True #change this to false to benchmark against bali_in
    i = 1 #start. End is dependent on what benchmark folder we use

    if (run_rv):
        test_path = Path("../RV100")
        for file in test_path.glob("*.tfa"):
            benchmark_tools(file,run_rv,i)
            i+=1
    else:
        print("Here!")
        test_path = Path("../bench1.0/bali3/in")
        for file in test_path.glob("*"):
            benchmark_tools(file,run_rv,i)
            i+=1
        