import sys
import os
from openpyxl import Workbook

wb = Workbook()
ws = wb.active
ws.append(['File Name', 'F-score'])

excel_file = 'accuracy_bali3.xlsx'

def calc_f(benchmark, inferred):
    tp = 0
    fp = 0
    fn = 0
    
    for benchmark_res, inferred_res in zip(benchmark, inferred):
        if benchmark_res == inferred_res and benchmark_res != '-':
            tp += 1
        elif benchmark_res == '-' and inferred_res != '-':
            fp += 1
        elif benchmark_res != '-' and inferred_res == '-':
            fn += 1

    precision = tp / (tp + fp) if (tp + fp) != 0 else 0
    recall = tp / (tp + fn) if (tp + fn) != 0 else 0
    
    if (precision + recall) == 0:
        return 0
    
    f = 2 * (precision * recall) / (precision + recall)

    return f

def read_alignment(path, is_benchmark=False):
    with open(path, 'r') as file:
        content = file.read().strip()

    sequence = ''.join(line for line in content.split('\n') if not line.startswith('>'))

    if is_benchmark:
        sequence = sequence.replace('.', '-')
    
    return sequence

def benchmark(benchmark_dir, inferred_dir, method):
    benchmark_files = sorted(os.listdir(benchmark_dir))
    
    for benchmark_file in benchmark_files:
        benchmark_path = os.path.join(benchmark_dir, benchmark_file)
        inferred_file = f"{benchmark_file}.aligned.fasta" if method == 'muscle' else f"merged_{benchmark_file}.fasta"
        inferred_path = os.path.join(inferred_dir, inferred_file)

        if not os.path.isfile(benchmark_path) or not os.path.isfile(inferred_path):
            continue
        
        benchmark_seq = read_alignment(benchmark_path, is_benchmark=True)
        inferred_seq = read_alignment(inferred_path, is_benchmark=False)

        f_inferred = calc_f(benchmark_seq, inferred_seq)

        print(f"F Score for {inferred_file}: {f_inferred:.4f}")
        ws.append([benchmark_file, f"{f_inferred:.4f}"])

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Proper format: python3 benchmark_acc.py <benchmark_dir> <inferred_dir> <MSA method (muscle/merge)>")
        sys.exit(1)

    benchmark_dir = sys.argv[1]
    inferred_dir = sys.argv[2]
    method = sys.argv[3]

    benchmark(benchmark_dir, inferred_dir, method)

wb.save(excel_file)