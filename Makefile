.PHONY: prep_min check_min help
PYTHON=$(shell which python)
SRC=$(NMT_HOME)/src
WP=$(shell grep "workPath:" $(shell pwd)/input.yaml | sed -E "s/.*workPath:[[:space:]]*'([^']+)'.*/\1/")
INPUT=$(shell grep "inputDirName:" $(shell pwd)/input.yaml | sed -E "s/.*inputDirName:[[:space:]]*'([^']+)'.*/\1/")


# Show help
help:
	@echo ""
	@echo -e "Usage: nemat <\033[31mtarget\033[0m>"
	@echo ""
	@echo "Targets:"
	@echo -e "  \033[31mwf\033[0m           :  Prints a schematic workflow and current step."
	@echo ""
	@echo -e "  \033[31mstart\033[0m        :  Prepare current directory for a NEMAT run. Provides default input.yaml and empty"
	@echo -e "                  folders for ligands and proteins along with the default mdppath and membrane."
	@echo ""
	@echo -e "  \033[31mprep\033[0m         :  Assembling the system"
	@echo ""
	@echo -e "  \033[31mprep_\033[0m\033[33m<step>\033[0m  :  step: \033[33mmin\033[0m, \033[33meq\033[0m, \033[33mmd\033[0m, \033[33mti\033[0m. Prepare input files for step."
	@echo ""
	@echo -e "  \033[31mcheck_\033[0m\033[33m<step>\033[0m :  step: \033[33mprep\033[0m, \033[33mmin\033[0m, \033[33meq\033[0m, \033[33mmd\033[0m, \033[33mti\033[0m, \033[33manalyze\033[0m. Check the logs/step.err file for any GROMACS errors."
	@echo ""
	@echo -e "  \033[31mrun_\033[0m\033[33m<step>\033[0m   :  step: \033[33mmin\033[0m, \033[33meq\033[0m, \033[33mmd\033[0m, \033[33mti\033[0m. Submits the job array to run the corresponding step."
	@echo ""
	@echo -e "  \033[31ms_\033[0m\033[33m<step>\033[0m     :  step: \033[33mmin\033[0m, \033[33meq\033[0m, \033[33mmd\033[0m, \033[33mti\033[0m. Check if the GROMACS run was successful."
	@echo ""
	@echo -e "  \033[31manalyze\033[0m      :  Analyze the results and produce the plots."
	@echo ""
	@echo -e "  \033[31mimg\033[0m          :  Generates all \"results images\" from pre-existing results_summary.csv files."
	@echo ""
	@echo -e "  \033[31mval\033[0m          :  Display the validation overlap checks from the analysis log."
	@echo ""
	@echo -e "  \033[31mnew\033[0m          :  Create a new run by removing the previous input and working directory files"
	@echo "                  (confirmation will be prompted)."
	@echo ""
	@echo -e "  \033[31mcopy\033[0m         :  Copy the current workpath directory in a new directory. Useful for example if you "
	@echo -e "                  want to use the same dynamics but change the number of transitions. You will be "
	@echo -e "                  prompted for the new destination path and the level of copying (eq, md or all)."
	@echo ""
	@echo -e "  \033[31mupdate\033[0m       :  Update NEMAT parameters in the current input directory to match those in input.yaml."
	@echo ""
	@echo -e "  \033[31mclean\033[0m        :  Clean up all backup files inside the workPath (confirmation will be prompted)."
	@echo ""
	@echo -e "  \033[31matom\033[0m         :  Provides file to solve minimization error."
	@echo ""
	@echo -e "  \033[31mcm\033[0m           :  Provides file to change protein b factor."
	@echo ""
	@echo -e "  \033[31mhelp\033[0m         :  Display this help message."
	@echo ""


# assembly system
prep:
	@rm -f logs/prep* logs/*prep.log
	@echo ">>> Preparing input files for assembly system..."
	@$(PYTHON) $(SRC)/NEMAT/file_gestor.py --step check --NMT_HOME $(NMT_HOME)
	@sbatch $(SRC)/NEMAT/run_files/prep.sh

# Check if there are any errors in the log
check_prep:
	@echo ">>> Checking for errors in assembly log..."
	@bash $(SRC)/NEMAT/check.sh prep
	@cat logs/checklist.txt

# Prepare minimization files
prep_min:
	@rm -f logs/min* logs/*min.log
	@echo ">>> Preparing minimization..."
	@sbatch $(SRC)/NEMAT/run_files/prep_min.sh

# Check if there are any errors in the log
check_min:
	@echo ">>> Checking for errors in minimization log..."
	@bash $(SRC)/NEMAT/check.sh min

run_min:
	@echo ">>> Running minimization..."
	@bash $(SRC)/NEMAT/run.sh $(WP) em $(job_id)

# Prepare equilibration files
prep_eq:
	@rm -f logs/eq* logs/*eq.log
	@echo ">>> Preparing equilibration..."
	@sbatch $(SRC)/NEMAT/run_files/prep_eq.sh

# Check if there are any errors in the log
check_eq:
	@echo ">>> Checking for errors in equilibration log..."
	@bash $(SRC)/NEMAT/check.sh eq

run_eq:
	@echo ">>> Running equilibration..."
	@bash $(SRC)/NEMAT/run.sh $(WP) eq $(job_id)

# Prepare production files
prep_md:
	@rm -f logs/md* logs/*md.log
	@echo ">>> Preparing production..."
	@sbatch $(SRC)/NEMAT/run_files/prep_md.sh

# Check if there are any errors in the log
check_md:
	@echo ">>> Checking for errors in production log..."
	@bash $(SRC)/NEMAT/check.sh md


run_md:
	@echo ">>> Running production..."
	@bash $(SRC)/NEMAT/run.sh $(WP) md $(job_id)

# Prepare transition files
prep_ti:
	@rm -f logs/ti* logs/*ti.log
	@echo ">>> Preparing transition..."
	@sbatch $(SRC)/NEMAT/run_files/prep_ti.sh

# Check if there are any errors in the log
check_ti:
	@echo ">>> Checking for errors in transition log..."
	@bash $(SRC)/NEMAT/check.sh ti

run_ti:
	@echo ">>> Running transition..."
	@bash $(SRC)/NEMAT/run.sh $(WP) transitions $(job_id)

# Analyze the results
analyze:
	@echo ">>> Analyzing results from $(WP)..."
	@rm -f logs/analysis* logs/*analysis.log
	@sbatch $(SRC)/NEMAT/run_files/analyze.sh $(WP)

check_analyze:
	@echo ">>> Checking for errors in analysis log..."
	@bash $(SRC)/NEMAT/check.sh analysis

img:
	@echo ">>> Generating image from pre-existing results_summary.csv..."
	@$(PYTHON) $(SRC)/NEMAT/file_gestor.py --step img

val:
	@echo ">>> Validating the overlap (good if >= 0.2)..."
	@$(PYTHON) $(SRC)/utils/overlap.py --wp $(WP)

s_min:
	@echo ">>> Checking for successful jobs in minimization..."
	@bash $(SRC)/utils/checkSuccessfullJobs.sh em

s_eq:
	@echo ">>> Checking for successful jobs in equilibration..."
	@bash $(SRC)/utils/checkSuccessfullJobs.sh eq

s_md:
	@echo ">>> Checking for successful jobs in production..."
	@bash $(SRC)/utils/checkSuccessfullJobs.sh md

s_ti:
	@echo ">>> Checking for successful jobs in transition..."
	@bash $(SRC)/utils/checkSuccessfullJobs.sh transitions

new:
	@bash $(SRC)/utils/new_run.sh $(INPUT) $(WP)

clean:
	@bash $(SRC)/utils/clean_backups.sh

copy:
	@echo ">>> Copying workPath ($(WP)) to a new destination..."
	@echo "Current working directory: $(shell pwd)"
	@read -p "Enter new (absolute) destination path: " dest; \
	read -p "Enter level (eq, md or all): " level; \
	bash $(SRC)/utils/copy_new.sh $(WP) $(INPUT) $$dest $$level

update:
	@echo ">>> Updating NEMAT parameters to match input.yaml..."
	@$(PYTHON) $(SRC)/NEMAT/file_gestor.py --step update --NMT_HOME $(NMT_HOME)
	@cat logs/checklist.txt


start:
	@bash $(SRC)/utils/start.sh


atom:
	@echo -e "\n>>> providing file find_atom.tcl..."
	@cp  $(SRC)/utils/find_atom.tcl .
	@echo -e ">>> file find_atom.tcl copied to current directory.\n"
	@echo -e "Use it in VMD to find atom indices as follows:"
	@echo -e "\t > Open the gro file that fails (e.g. membrane.gro) with VMD"
	@echo -e "\t > Open find_atoms.tcl and change the atom index on the first line (0-based)"
	@echo -e "\t > Then, at the VMD command prompt, type: \033[1;33msource find_atom.tcl\033[0m"
	@echo -e "\t > The atom will be highlighted in red. Move it to avoid crashes\n"


cm:
	@echo -e "\n>>> providing file membrane_bfactor.py..."
	@cp  $(SRC)/utils/membrane_bfactor.py .
	@echo -e ">>> file membrane_bfactor.py copied to current directory.\n"
	@echo -e "Use it to change values of the protein b factor:"
	@echo -e "\t > Provide the FASTA of your protein to https://services.healthtech.dtu.dk/services/DeepTMHMM-1.0/ to predict membrane regions"
	@echo -e "\t > Copy the output sequence (with M, I, O letters) to the file membrane_bfactor.py"
	@echo -e "\t > Change the protein input and output name inside membrane_bfactor.py"
	@echo -e "\t > Use 'python membrane_bfactor.py'\n"


example:
	@echo ">>> Preparing example..."
	@bash $(SRC)/utils/example.sh $(NMT_HOME)


wf:
	@bash $(SRC)/utils/current_step.sh $(WP)




