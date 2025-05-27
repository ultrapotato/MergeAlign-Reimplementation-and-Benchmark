import argparse
import os
from Bio import AlignIO
from Bio.Align import MultipleSeqAlignment
from Bio.SeqRecord import SeqRecord
from Bio.Align import AlignInfo

def read_alignments(alignment_folder_path):
    """
    Reads all MAFFT alignment files from a folder and returns a list of AlignIO objects.
    """
    alignments = []
    alns2 = None
    for filename in os.listdir(alignment_folder_path):
        if filename.endswith(".aln"): 
            filepath = os.path.join(alignment_folder_path, filename)
            alignment = AlignIO.read(filepath, "fasta")
            if (alns2 is None):
               alns2 = [[] for _ in alignment]
            for i,record in enumerate(alignment):
               alns2[i].append(record)
            alignments.append(alignment)

    alignment_length = max(len(aln[0]) for aln in alignments)

    for alignment in alns2:
      for record in alignment:
        if len(record) < alignment_length:
          record.seq = record.seq + "-" * (alignment_length - len(record))
    alns3 = [MultipleSeqAlignment(aln) for aln in alns2]
    AlignIO.write(alns3, "bench_temp_folder/temp.fasta","fasta")
    all2 = AlignIO.parse("bench_temp_folder/temp.fasta","fasta",seq_count=len(alignments))
    aligns = []
    for sq in all2:
       aligns.append(sq)
    return aligns

def create_consensus_alignment(alignments):
    """
    Creates a consensus alignment from a list of MAFFT alignments.
    """
    summaries = [AlignInfo.SummaryInfo(aln) for aln in alignments]    
    consensus_alignment = [SeqRecord(cons.dumb_consensus(ambiguous='-')) for cons in summaries]
    return MultipleSeqAlignment(consensus_alignment)

def write_consensus_alignment(consensus_alignment, output_file):
    """
    Writes the consensus alignment to a file.
    """
    with open(output_file, "w") as out_file:
        AlignIO.write(consensus_alignment, out_file, "fasta")

def main():
    parser = argparse.ArgumentParser(description="Run BioAlign")
    parser.add_argument("alignment_folder_path", help="Path to the input fasta file")
    parser.add_argument("output_dir", help="Path to the input fasta file")
    parser.add_argument("output_file", help="Path to the input fasta file")
    # alignment_folder_path = "mafft_alignments"
    output_file = "consensus_alignment.fasta" 
    args = parser.parse_args()

    alignments = read_alignments(args.alignment_folder_path)
    consensus_alignment = create_consensus_alignment(alignments)
    write_consensus_alignment(consensus_alignment, args.output_dir+"/"+args.output_file + "_" + output_file)
    print(f"Consensus alignment written to {output_file}")

if __name__ == "__main__":
    main()
