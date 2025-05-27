def parse_fasta(filename):
    """Parse FASTA format alignment with debug output."""
    sequences = {}
    current_id = None
    
    with open(filename) as f:
        for line in f:
            line = line.strip()
            if line.startswith('>'):
                current_id = line[1:].split()[0]  
                sequences[current_id] = ''
            elif current_id is not None:
                sequences[current_id] += line.replace('.', '-')  
    
    return sequences

def calculate_alignment_scores(test_file, ref_file, debug=False):
    """Calculate alignment scores with debug info."""
    test_seqs = parse_fasta(test_file)
    ref_seqs = parse_fasta(ref_file)
    
    if debug:
        print("\nDebug Info:")
        print(f"Test sequences: {len(test_seqs)}")
        print(f"Ref sequences: {len(ref_seqs)}")
        print(f"Common IDs: {len(set(test_seqs.keys()) & set(ref_seqs.keys()))}")
        if test_seqs:
            first_test = next(iter(test_seqs.values()))
            print(f"Test alignment length: {len(first_test)}")
        if ref_seqs:
            first_ref = next(iter(ref_seqs.values()))
            print(f"Ref alignment length: {len(first_ref)}")
    
    test_pairs = set()
    ref_pairs = set()
    
    common_ids = set(test_seqs.keys()) & set(ref_seqs.keys())
    
    for id1 in common_ids:
        for id2 in common_ids:
            if id1 >= id2:
                continue
            
            seq1_test = test_seqs[id1]
            seq2_test = test_seqs[id2]
            seq1_ref = ref_seqs[id1]
            seq2_ref = ref_seqs[id2]
            
            # Get aligned positions
            pos1, pos2 = 0, 0
            for i in range(len(seq1_test)):
                if seq1_test[i] != '-' and seq2_test[i] != '-':
                    test_pairs.add((f"{id1}_{pos1}", f"{id2}_{pos2}"))
                if seq1_test[i] != '-':
                    pos1 += 1
                if seq2_test[i] != '-':
                    pos2 += 1
            
            pos1, pos2 = 0, 0
            for i in range(len(seq1_ref)):
                if seq1_ref[i] != '-' and seq2_ref[i] != '-':
                    ref_pairs.add((f"{id1}_{pos1}", f"{id2}_{pos2}"))
                if seq1_ref[i] != '-':
                    pos1 += 1
                if seq2_ref[i] != '-':
                    pos2 += 1
    
    tp = len(test_pairs & ref_pairs)
    fp = len(test_pairs - ref_pairs)
    fn = len(ref_pairs - test_pairs)
    
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f_score = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    
    if debug:
        print(f"TP: {tp}, FP: {fp}, FN: {fn}")
        print(f"Precision: {precision:.4f}, Recall: {recall:.4f}, F-score: {f_score:.4f}")
    
    return {'precision': precision, 'recall': recall, 'f_score': f_score}