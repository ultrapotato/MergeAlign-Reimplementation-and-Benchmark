import os
import random
from pathlib import Path
import subprocess
import re
import json
from datetime import datetime
import time
import urllib.request
import urllib.parse
from alignment_scoring import calculate_alignment_scores

def parse_matrix_list(filename):
    matrices = []
    with open(filename, 'r') as f:
        for line in f:
            match = re.match(r'^([A-Z]+\d+)', line)
            if match:
                matrices.append(match.group(1))
    return matrices



def create_matrix_file(matrix_id, matrix_data):
    matrix_dir = Path('mergealign_matrices')
    matrix_dir.mkdir(exist_ok=True)
    matrix_file = matrix_dir / matrix_id
    
    amino_acids = 'ARNDCQEGHILKMFPSTWYV'
    with open(matrix_file, 'w') as f:
        f.write(f"# {matrix_id}\n")
        f.write(f"   {' '.join(amino_acids)}\n")
        for aa in amino_acids:
            f.write(f"{aa}  {' '.join(map(lambda x: f'{x:.2f}', matrix_data[aa]))}\n")
    
    return matrix_file

def collect_all_msas():
    all_msas = []
    base_dir = Path('bench1.0')
    benchmark_dirs = {
        'bali3': {'in': 'in', 'ref': 'ref'},
        'sabre': {'in': 'in', 'ref': 'ref'},
        'ox': {'in': 'in', 'ref': 'ref'}
    }
    
    for bench_dir, paths in benchmark_dirs.items():
        input_dir = base_dir / bench_dir / paths['in']
        ref_dir = base_dir / bench_dir / paths['ref']
        
        if not input_dir.exists() or not ref_dir.exists():
            print(f"Warning: Directory not found: {input_dir} or {ref_dir}")
            continue
            
        for file in input_dir.iterdir():
            ref_file = ref_dir / file.name
            if ref_file.exists():
                all_msas.append((file, ref_file))
                
    print(f"Found {len(all_msas)} total MSAs")
    return all_msas

def parse_matrix_raw(matrix_text):
    matrix_data = {}
    amino_acids = 'ARNDCQEGHILKMFPSTWYV'
    
    rows = [line.strip() for line in matrix_text.strip().split('\n') if line.strip()]
    
    if len(rows) == 19:  
        values = []
        for row in rows:
            nums = re.findall(r'-?\d+\.?\d*', row)
            vals = [float(n) for n in nums]
            while len(vals) < 20:
                vals.append(0.0)
            values.extend(vals)
        if len(values) < 400:
            values.extend([0.0] * 20)
            
        for i, aa in enumerate(amino_acids):
            matrix_data[aa] = values[i*20:(i+1)*20]
        return matrix_data
    
    values = []
    for row in rows:
        row = re.sub(r'(\d+)\.(?!\d)', r'\1.0', row)
        nums = re.findall(r'-?\d+\.?\d*', row)
        if nums:
            values.extend([float(n) for n in nums])
    
    if len(values) == 210: 
        full_matrix = [[0.0] * 20 for _ in range(20)]
        idx = 0
        for i in range(20):
            for j in range(i + 1):
                val = values[idx]
                full_matrix[i][j] = val
                full_matrix[j][i] = val
                idx += 1
        
        for i, aa in enumerate(amino_acids):
            matrix_data[aa] = full_matrix[i]
            
    elif len(values) >= 200:  # Full matrix
        rows = [values[i:i+20] for i in range(0, min(400, len(values)), 20)]
        for i, aa in enumerate(amino_acids):
            if i < len(rows):
                row = rows[i]
                while len(row) < 20:
                    row.append(0.0)
                matrix_data[aa] = row[:20]
            else:
                matrix_data[aa] = [0.0] * 20
                
    if not matrix_data:
        raise ValueError(f"Invalid matrix format: {len(values)} values found")
        
    return matrix_data

def fetch_matrix_data(matrix_id):
    url = f"https://www.genome.jp/dbget-bin/www_bget?aaindex:{matrix_id}"
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as response:
            html = response.read().decode('utf-8')
            
            matrix_text = ""
            in_matrix = False
            for line in html.split('\n'):
                if 'M rows = ' in line and 'cols = ' in line:
                    in_matrix = True
                    continue
                elif in_matrix and '//' in line:
                    break
                elif in_matrix:
                    cleaned = re.sub(r'<[^>]+>', '', line).strip()
                    if cleaned and any(c.isdigit() or c in '.-' for c in cleaned):
                        matrix_text += cleaned + "\n"
            
            return matrix_text if matrix_text else None
            
    except Exception as e:
        print(f"Error fetching matrix {matrix_id}: {e}")
        return None

def run_benchmark(matrix_id, matrix_data, benchmark_msas, output_dir):
    scores = []
    
    matrix_file = create_matrix_file(matrix_id, matrix_data)  
    
    for idx, (input_file, ref_file) in enumerate(benchmark_msas):
        output_file = output_dir / f"{input_file.stem}_{matrix_id}.aln"
        
        cmd = [
            'mafft',
            '--amino',
            '--quiet',
            '--retree', '2',
            '--maxiterate', '0',
            '--aamatrix', str(matrix_file),
            str(input_file)
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            with open(output_file, 'w') as f:
                f.write(result.stdout)
                
            score = calculate_alignment_scores(output_file, ref_file)
            scores.append(score)
            
        except Exception as e:
            print(f"Error processing {input_file} with {matrix_id}: {e}")
    
    if scores:
        avg_scores = {
            'f_score': sum(s['f_score'] for s in scores) / len(scores),
            'precision': sum(s['precision'] for s in scores) / len(scores),
            'recall': sum(s['recall'] for s in scores) / len(scores)
        }
        return avg_scores
    return None

def main():
    output_dir = Path(f'benchmark_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
    output_dir.mkdir(exist_ok=True)
    
    all_msas = collect_all_msas()
    if len(all_msas) < 10:
        print("Warning: Found fewer than 10 MSAs")
        benchmark_msas = all_msas
    else:
        benchmark_msas = random.sample(all_msas, 10)
        
    print(f"Selected {len(benchmark_msas)} MSAs for benchmarking")
    
    matrices = parse_matrix_list('list_of_matrices.txt')
    print(f"Testing {len(matrices)} matrices")
    
    results = {}
    
    for matrix_idx, matrix_id in enumerate(matrices, 1):
        print(f"\nProcessing matrix {matrix_idx}/{len(matrices)}: {matrix_id}")
        
        matrix_text = fetch_matrix_data(matrix_id)
        if not matrix_text:
            print(f"Failed to fetch matrix {matrix_id}")
            continue
            
        try:
            matrix_data = parse_matrix_raw(matrix_text)
            scores = run_benchmark(matrix_id, matrix_data, benchmark_msas, output_dir)
            if scores:
                results[matrix_id] = scores
                print(f"Average F-score: {scores['f_score']:.4f}")
            
            time.sleep(1) 
            
        except Exception as e:
            print(f"Error processing matrix {matrix_id}: {e}")
    
    with open(output_dir / 'benchmark_msas.txt', 'w') as f:
        for input_file, ref_file in benchmark_msas:
            f.write(f"{input_file}\t{ref_file}\n")
    
    sorted_matrices = sorted(results.items(), 
                           key=lambda x: x[1]['f_score'], 
                           reverse=True)
    
    print("\nMatrix rankings:")
    with open(output_dir / 'matrix_rankings.txt', 'w') as f:
        f.write("Matrix\tF-score\tPrecision\tRecall\n")
        for matrix, scores in sorted_matrices:
            line = f"{matrix}\t{scores['f_score']:.4f}\t{scores['precision']:.4f}\t{scores['recall']:.4f}"
            f.write(line + '\n')
            print(line)
    
    with open(output_dir / 'detailed_results.json', 'w') as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    main()