# Replace this with your actual atom index
set atomIndex 118

# Select the specific atom by index
set atomSel [atomselect top "index $atomIndex"]
$atomSel set beta 0.0  ;# Dummy command to force update

# Create a representation for the single atom
mol selection "index $atomIndex"
mol representation Licorice
mol color ColorID 1  ;# Red
mol material Opaque
mol addrep top

# Select all atoms with resname LIG
set ligSel [atomselect top "resname LIG"]
$ligSel set beta 0.0  ;# Force update again

# Create representation for LIG
mol selection "resname LIG"
mol representation Licorice
mol color ColorID 7  ;# Green
mol material Opaque
mol addrep top
