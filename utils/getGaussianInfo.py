"""
For a given workpath, returns a .txt file containing the mean and standard deviation 
of the work distributions for each replicate.

"""

import sys 
import os 
import numpy as np
import pandas as pd

def get_gauss_info(file):
    """
    Extract the mean and standard deviation from a set of data
    """
    data = np.loadtxt(file, usecols=1)
    mean = data.mean()
    std = data.std()
    return mean, std, data


workpath = sys.argv[1]

# Get the path where the analysis data of the work distributions are stored
analyse_dirs = []
for (dirpath, dirnames, filenames) in os.walk(workpath):
    if "analyse" in dirpath:
        analyse_dirs.append(dirpath)

# print(analyse_dirs)

df = pd.DataFrame(columns=["workpath", "edge", "mode", "replica", "direction", "data"])

with open(os.path.join(workpath, "work_distribution_stats.txt"), "w") as file:
    file.write("WORK DISTRIBUTION INFO\n")
    file.write(f"Workpath: {workpath}\n")
    file.write("=============================================\n")

    for dir in analyse_dirs:

        forward = os.path.join(dir, "integ0.dat")
        mean_forward, std_forward, data_forward = get_gauss_info(forward)

        backward = os.path.join(dir, "integ1.dat")
        mean_backward, std_backward, data_backwards = get_gauss_info(backward)

        # Write the results to a.txt file

        file.write(f"{dir}\n")
        file.write(f" \t FORWARD: mean = {mean_forward:+.3f} std = {std_forward:+.3f}\n")
        file.write(f" \t BACKWARD: mean = {mean_backward:+.3f} std = {std_backward:+.3f}\n")
        file.write("\n")

        # Save all the data points in a dataframe for posterior analysis.
        components = dir.split(os.path.sep)
        workspace, edge, mode, replica = components

        rows_f = [{"workpath": workspace, 
                    "edge": edge, 
                    "mode": mode, 
                    "replica": replica, 
                    "direction": "forward", 
                    "data": dd} for dd in data_forward]
        df_f = pd.DataFrame(rows_f)
        
        rows_b = [{"workpath": workspace, 
                    "edge": edge, 
                    "mode": mode, 
                    "replica": replica, 
                    "direction": "backwards", 
                    "data": dd} for dd in data_backwards]
        df_b = pd.DataFrame(rows_b)

        df = pd.concat([df,df_f, df_b]) 

# Save the dataframe to a.csv file
name=f"gauss_{workpath}.csv"
df.to_csv(os.path.join("gauss_dfs", name), index=False)

print("Analysis completed successfully.")




