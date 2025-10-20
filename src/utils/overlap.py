import numpy as np
import os
from argparse import ArgumentParser

def args_parser():
    """
    This function parses command-line arguments for the script.

    Parameters:
    -----------
    None

    Returns:
    --------
    args : argparse.Namespace
        An object containing the parsed command-line arguments.
        The object has attributes corresponding to the command-line arguments,
        e.g., args.p
    """
    parser = ArgumentParser()
    parser.add_argument(
        "--wp",
        type=str,
        help="Path to the working directory.",
        required=True,
    )

    args = parser.parse_args()
    return args

def load_dat(filename):
    """Load the second column from a .dat file (two columns, space-separated)."""
    data = []
    with open(filename) as f:
        for line in f:
            if line.strip() == "":
                continue
            parts = line.split()
            if len(parts) >= 2:
                data.append(float(parts[1]))  # take 2nd column
    return np.array(data)

def overlap_score(file1, file2, bins=100):
    """Compute overlap integral between two distributions in .dat files."""
    data1 = load_dat(file1)
    data2 = load_dat(file2)

    # Build histograms over the same range
    hist_range = (min(data1.min(), data2.min()), max(data1.max(), data2.max()))
    p1, edges = np.histogram(data1, bins=bins, range=hist_range, density=True)
    p2, _     = np.histogram(data2, bins=bins, range=hist_range, density=True)

    dx = edges[1] - edges[0]

    overlap = np.sum(np.minimum(p1, p2)) * dx
    return overlap

# Example usage:

if __name__ == "__main__":
    args = args_parser()
    
    red = "\033[31m"
    green = "\033[92m"
    end = "\033[0m"

    edges = os.listdir(args.wp)
    edges = [e for e in edges if e.startswith("edge_")]
    le = max(len(e.lstrip('edge_')) for e in edges)

    for e in edges:
        for syst in ['water', 'membrane', 'protein']:
            analysis = os.listdir(os.path.join(args.wp, e, syst))
            analysis = [a for a in analysis if a.startswith("analyse")]
            tl = 7 + le + 8 + 8 + 11 + 3 + 16 + 15
            print('+-' + '-' * tl + '+')
            for a in analysis:
                f1 = os.path.join(args.wp, e, syst, a, "integ0.dat")
                f2 = os.path.join(args.wp, e, syst, a, "integ1.dat")
                if os.path.exists(f1) and os.path.exists(f2):
                    score = overlap_score(f1, f2)
                    if score < 0.2:
                        color = red 
                    else:
                        color = green
                    print(f"| Edge: {e.lstrip('edge_'):{le}}\t System: {syst:8}\t Analysis: {a.lstrip('analyse'):3}\t Overlap score: {color}{score:.2f}{end} |")
            print('+-' + '-' * tl + '+')
        print('\n')