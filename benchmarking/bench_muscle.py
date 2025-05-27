import os
import subprocess
import time
import psutil
from openpyxl import Workbook

muscle_executable = '/Users/gavinzhou/opt/anaconda3/bin/muscle' # NOTE: Change this to path to MUSCLE executable before running
input_folder = 'bali_in' # can modify before running
output_folder = 'muscle_alignments' # can modify before running
excel_file = 'muscle_speed.xlsx' # can modify before running

os.makedirs(output_folder, exist_ok=True)

wb = Workbook()
ws = wb.active
ws.append(['File Name', 'Runtime (s)', 'Memory Usage (MB)', 'Peak Memory Usage (MB)'])

def get_memory_usage():
    process = psutil.Process(os.getpid())
    mem_info = process.memory_info()
    return mem_info.rss / 1024 / 1024

for file_name in os.listdir(input_folder):
    file_path = os.path.join(input_folder, file_name)
    
    if os.path.isfile(file_path) and not '.' in file_name:
    #if os.path.isfile(file_path) and file_name.endswith('.tfa'):
        output_file = os.path.join(output_folder, f"{file_name}.aligned.fasta")
        
        start_time = time.time()
        start_memory = get_memory_usage()

        try:
            subprocess.run([muscle_executable, '-align', file_path, '-output', output_file], check=True)
            runtime = time.time() - start_time
            peak_memory = get_memory_usage() - start_memory
            print(f"Success, {file_name} completed in {runtime:.2f}s, peak memory usage of {peak_memory:.2f}MB.")
            ws.append([file_name, f"{runtime:.2f}", f"{start_memory:.2f}", f"{peak_memory:.2f}"])
        
        except subprocess.CalledProcessError as e:
            print(f"Error, {file_name}: {e}")
        
wb.save(excel_file)
