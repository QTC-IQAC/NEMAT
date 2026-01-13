
mol new protein.pdb
mol new system.pdb

# ==============================
# USER PARAMETERS
# ==============================
set single_name  "protein.pdb"
set system_name  "system.pdb"

# ==============================
# GET MOLECULE IDS
# ==============================
set single_id -1
set system_id -1

foreach mid [molinfo list] {
    set name [molinfo $mid get name]
    if {$name eq $single_name} { set single_id $mid }
    if {$name eq $system_name} { set system_id $mid }
}

if {$single_id == -1} {
    error "Single protein '$single_name' not found."
}
if {$system_id == -1} {
    error "System protein '$system_name' not found."
}


# ==============================
# ALIGN SINGLE ONTO SYSTEM
# ==============================
set ref_sel  [atomselect $system_id "name CA and segname PROA A"]
set mov_sel  [atomselect $single_id "name CA and segname PROA A"]

if {[$ref_sel num] == 0 || [$mov_sel num] == 0} {
    error "Alignment selection returned zero atoms. Check segname and atom names."
}

set M [measure fit $mov_sel $ref_sel]
set all_single [atomselect $single_id all]
$all_single move $M

$ref_sel delete
$mov_sel delete
$all_single delete

# ==============================
# SINGLE PROTEIN REPRESENTATION
# QuickSurf colored by Beta
# ==============================
mol delrep 0 $single_id
mol representation QuickSurf
mol color Beta
mol selection all
mol material Opaque
mol addrep $single_id

# ==============================
# SYSTEM REPRESENTATIONS
# ==============================

# Delete default rep
mol delrep 0 $system_id

# --- Protein as NewCartoon ---
mol representation NewCartoon
mol color Structure
mol selection protein
mol material Opaque
mol addrep $system_id

# --- Non-protein as VDW ---
mol representation VDW
mol color Name
mol selection "not protein"
mol material Opaque
mol addrep $system_id

# ==============================
# DISPLAY SETTINGS
# ==============================

# Orthographic projection
display projection Orthographic

# Enable Tape Measure (Ruler)
set ruler
# Optional: improve rendering quality
display rendermode GLSL
axes location Off

puts "Visualization setup completed successfully."
