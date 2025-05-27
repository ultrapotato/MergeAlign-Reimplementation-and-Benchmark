#!/usr/bin/python

"""
MergeAlign algorithm for consensus multiple sequence alignments
"""

import os
import sys
import getopt

class Node:
    """ A position in alignment space with edges to the previous nodes in all alignments """
    
    def __init__(self):
        self.previous_nodes = [] 
        self.path_score = 0
        self.path_length = 0
        self.path_average = 0
        self.best_previous_node = None

def parse_fasta(filename):
    """Read FASTA file and return list of (seq_id, sequence) tuples"""
    try:
        with open(filename, 'r') as f:
            lines = f.readlines()
    except IOError:
        print(f"Unable to open file {filename}")
        sys.exit(2)

    sequences = []
    seq_id = None

    for line in lines:
        if line.startswith('>'):
            seq_id = line.rstrip()[1:]
            sequences.append((seq_id, ''))
        elif seq_id is not None:
            seq = sequences[-1][1] + line.rstrip()
            sequences[-1] = (seq_id, seq)

    if len(sequences) == 0:
        print(f"{filename} contains no sequences")
        sys.exit(2)

    return sequences

def convert_to_indices(sequence):
    """Convert sequence to position indices"""
    indices = []
    pos = 0
    for char in sequence:
        if char != '-':
            pos += 1
        indices.append(pos)
    return indices

def convert_indices_to_sequence(indices, original_sequence):
    """Convert indices back to sequence with gaps"""
    sequence = ''
    prev_i = 0
    
    for i in indices:
        if i != prev_i:
            sequence += original_sequence[i-1]
        else:
            sequence += '-'
        prev_i = i
        
    return sequence

def create_nodes(coordinates):
    """Create nodes from alignment coordinates"""
    if not coordinates or not coordinates[0]:
        raise ValueError("Empty alignments provided")
    
    dimensions = len(coordinates[0][0])
    print(f"Dimensions: {dimensions}")
    
    start_node = tuple([0] * dimensions)
    nodes = {start_node: Node()}
    
    for alignment in coordinates:
        prev_node = start_node
        for point in alignment:
            if point not in nodes:
                nodes[point] = Node()
            
            prev_nodes_list = nodes[point].previous_nodes
            for idx, (node, count) in enumerate(prev_nodes_list):
                if node == prev_node:
                    prev_nodes_list[idx] = (node, count + 1)
                    break
            else:
                prev_nodes_list.append((prev_node, 1))
            
            prev_node = point
                
    return nodes

def score_nodes(nodes, num_paths=100):
    """Score nodes and find optimal path"""
    dimensions = len(next(iter(nodes)))
    start_node = tuple([0] * dimensions)
    sorted_coords = sorted(nodes.keys())
    
    for coord in sorted_coords[1:]:
        current_node = nodes[coord]
        prev_nodes = current_node.previous_nodes 
        best_node = max(prev_nodes, key=lambda n: n[1] + nodes[n[0]].path_average)
        
        prev_node_coord = best_node[0]
        current_node.path_length = nodes[prev_node_coord].path_length + 1
        current_node.path_score = best_node[1] + nodes[prev_node_coord].path_score
        current_node.path_average = current_node.path_score / current_node.path_length
        current_node.best_previous_node = prev_node_coord
    
    path = []
    scores = []
    coord = sorted_coords[-1] 
    while coord != start_node:
        path.append(coord)
        current_node = nodes[coord]
        prev_node = current_node.best_previous_node
        for node, count in current_node.previous_nodes:
            if node == prev_node:
                break
        else:
            count = 0 
        
        scores.append(count / num_paths)
        coord = prev_node

    path.reverse()
    scores.reverse()
    return path, scores

def convert_coordinates_to_sequences(coordinates, original_sequences):
    """Convert coordinates to final alignment"""
    seq_names = [name for name, _ in original_sequences]
    alignment = {}
    
    for idx, sequence_indices in enumerate(zip(*coordinates)):
        seq_name = seq_names[idx]
        original_seq = next(seq for name, seq in original_sequences if name == seq_name)
        alignment[seq_name] = convert_indices_to_sequence(sequence_indices, original_seq)
        
    return alignment
    
def combine_alignments(alignment_names):
    """Main function to combine multiple alignments"""
    alignments = []
    for filename in alignment_names:
        try:
            aln = parse_fasta(filename)
            if aln:
                alignments.append(aln)
                print(f"Successfully read: {filename}")
            else:
                print(f"Warning: Empty alignment in {filename}")
        except Exception as e:
            print(f"Error reading {filename}: {e}")
    
    if not alignments:
        raise ValueError("No valid alignments were read")
    
    original_sequences = [(name, seq.replace('-', '')) for name, seq in alignments[0]]
    sequence_names = [name for name, _ in original_sequences]
    
    print(f"Number of sequences: {len(sequence_names)}")
    print(f"First sequence name: {sequence_names[0] if sequence_names else 'None'}")
    
    indices = []
    for alignment in alignments:
        try:
            seq_dict = dict(alignment)
            index_list = [convert_to_indices(seq_dict[seq]) for seq in sequence_names]
            indices.append(index_list)
        except Exception as e:
            print(f"Error converting sequences to indices: {e}")
        
    coordinates = []
    for alignment in indices:
        coord = list(zip(*alignment))
        coordinates.append(coord)
    
    if not coordinates:
        raise ValueError("No valid coordinates were generated")
    
    print(f"Number of coordinate sets: {len(coordinates)}")
    
    nodes = create_nodes(coordinates)
    final_coordinates, scores = score_nodes(nodes, len(coordinates))
    final_alignment = convert_coordinates_to_sequences(final_coordinates, original_sequences)
    
    return final_alignment, scores

def write_fasta(filename, alignment, threshold=None, scores=None):
    """Write alignment to FASTA file"""
    with open(filename, 'w') as f:
        for name, sequence in alignment.items():
            f.write(f">{name}\n")
            if threshold is not None and scores is not None:
                sequence = ''.join([aa for aa, score in zip(sequence, scores) if score > threshold])
            f.write(f"{sequence}\n")
    
def write_score(filename, scores):
    """Write scores to file"""
    with open(filename, 'w') as f:
        for score in scores:
            f.write(f"{score:.3f}\n")
    
if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:],
                                 "ha:f:s:t:",
                                 ["help", "alignments=", "fasta=", "score=", "threshold="])
    except getopt.GetoptError:
        print("Error: command line argument not recognised")
        sys.exit(2)

    alignment_folder = None
    fasta_output = None
    score_output = None
    threshold = None
    
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            sys.exit()
        elif opt in ("-a", "--alignments"):
            alignment_folder = arg
        elif opt in ("-f", "--fasta"):
            fasta_output = arg
        elif opt in ("-s", "--score"):
            score_output = arg
        elif opt in ("-t", "--threshold"):
            try:
                threshold = float(arg)
                if not 0 < threshold <= 1:
                    print('Error: threshold must be >0 and <= 1')
                    sys.exit(2)
            except ValueError:
                print('Error: threshold must be a number')
                sys.exit(2)
    
    if not alignment_folder:
        print("Error: alignment folder not defined")
        sys.exit(2)

    alignment_names = [os.path.join(alignment_folder, f) 
                      for f in os.listdir(alignment_folder)]
    final_alignment, scores = combine_alignments(alignment_names)
    
    if fasta_output:
        write_fasta(fasta_output, final_alignment, threshold, scores)
    if score_output:
        write_score(score_output, scores)
