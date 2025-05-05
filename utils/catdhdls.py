import numpy as np
import sys 
import os
    
print(os.getcwd())
num = int(sys.argv[1])

last_time = 0
data_list = [] 
for ii in range(1,4):
    file = open(f"wlist{num}-{ii}.xvg","r")
    data = np.loadtxt(file, comments=["@","#"])

    # change first column time (to make it sequential)
    data[:,0] = last_time + data[:,0]
    last_time = data[-1,0]

    # remove first line of data (avoid repetition of data)
    if ii > 1:
        data = data[1:,:]
    
    data_list.append(data)


full_data = np.concatenate(data_list,axis=0)
np.savetxt(f"dhdl{num}.xvg",full_data,fmt="%.5f")

print(f"dhdl{num}.xvg created!")