#!/usr/bin/env python3

def parse_gro_resnames(filename):
    resnames = set()

    with open(filename) as f:
        lines = f.readlines()

    # Skip header (line 0) and atom count (line 1), skip box vector (last line)
    atom_lines = lines[2:-1]

    for line in atom_lines:
        # Residue number: chars 0:5
        # Residue name : chars 5:10
        resname = line[5:10].strip()
        resnames.add(resname)

    return resnames


def find_lipids(gro):
    PROTEIN_RESNAMES = {
    "ALA","ARG","ASN","ASP","CYS","GLN","GLU","GLY","HIS",
    "ILE","LEU","LYS","MET","PHE","PRO","SER","THR","TRP",
    "TYR","VAL", "HID", "HIE", "HIP", "LYN", "ASH", "GLH", "CYM", "CYX"
    }
    resnames = parse_gro_resnames(gro)

    # Identify non-protein residues
    nonprotein = list(r for r in resnames if r.upper() not in PROTEIN_RESNAMES)
    nonprotein = list(r for r in nonprotein if r[1:] not in PROTEIN_RESNAMES)


    # print("Found the following non-protein residue types:\n")
    # for r in nonprotein:
    #     print("  -", r)

    return len(nonprotein)-4 # subtract 4 for SOL, ION+, ION-, LIG


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python read_gro.py file.gro")
        sys.exit(1)
    
    gro = sys.argv[1]
    find_lipids(gro)

