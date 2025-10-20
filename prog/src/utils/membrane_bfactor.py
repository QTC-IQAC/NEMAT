import sys

def update_bfactors(pdb_path, code_string, output_path):
    with open(pdb_path, 'r') as f:
        lines = f.readlines()

    updated_lines = []
    res_seq_seen = []
    code_index = 0

    for line in lines:
        if line.startswith("ATOM") or line.startswith("HETATM"):
            res_seq = line[22:26]
            chain_id = line[21]

            # Create a unique key per residue (chain + resnum)
            key = (chain_id, res_seq)
            if key not in res_seq_seen:
                res_seq_seen.append(key)
                code_index += 1

            # Assign B-factor based on code
            code = code_string[res_seq_seen.index(key)]
            if code == 'M':
                b = 0.5
            elif code == 'O':
                b = 1.0
            elif code == 'I':
                b = 0.0
            else:
                raise ValueError(f"Invalid code '{code}' in code string.")

            # Replace B-factor field (60–66)
            new_line = line[:60] + f"{b:6.2f}" + line[66:]
            updated_lines.append(new_line)
        else:
            updated_lines.append(line)

    with open(output_path, 'w') as f:
        f.writelines(updated_lines)

    print(f"Modified PDB saved as: {output_path}")

# Example usage
if __name__ == "__main__":
    # Provide input PDB, code string, and output file name
    input_pdb = "prot.pdb"
    code_string = "IMMMMMMMMMMMMMMMMMOOOOOOOOOOMMMMMMMMMMMMMMMMMMMMMIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII"  # Replace with your actual string
    output_pdb = "prot.pdb"
    update_bfactors(input_pdb, code_string, output_pdb)