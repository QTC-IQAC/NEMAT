import matplotlib.pyplot as plt
import numpy as np
import os

def make_plot(filename,outname):
    """
    Load and plot a given XVG file containing data for a free energy calculation.

    Parameters
    ----------
    """
    data = np.loadtxt(filename, skiprows=20, comments="@")
    plt.plot(data[:,0], data[:,1],label="dH/dl")
    plt.legend()
    plt.title(filename)
    plt.savefig(f"{outname}")
    plt.clf()

# file = "/home/ramon/berta/aztuto/workpath_hpgr/edge_LVG_wH_RU486_wH/water/stateB/run2/transitions/dhdl68.xvg"

# data = np.loadtxt(file, skiprows=20, comments="@")
# # data = data[10:,:]

# # plt.plot(data[:,0], data[:,1],label="Potential Energy")
# plt.plot(data[:,0], data[:,1],label="dH/dl")
# # plt.plot(data[:,0], data[:,2],label="Kinetic Energy")
# # plt.plot(data[:,0], data[:,3],label="Total Energy")
# plt.legend()
# # plt.xlabel("lambda")
# # plt.ylabel("Energy (kJ/mol)")
# plt.title(file)
# plt.savefig("ener_plot_A_ti.png")

stateA = "/home/ramon/berta/aztuto/workpath_hpgr/edge_P4_wH_LVG_wH/protein/stateA/run1/transitions"
stateB = "/home/ramon/berta/aztuto/workpath_hpgr/edge_P4_wH_LVG_wH/protein/stateB/run1/transitions"
for ii in range(1,81):
    name = f"dhdl{ii}"
    fileA = os.path.join(stateA,name+".xvg")
    fileB = os.path.join(stateB,name+".xvg")

    make_plot(fileA, "plotsAP4/"+name+".png")
    make_plot(fileB, "plotsBP4/"+name+".png")