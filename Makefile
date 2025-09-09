.PHONY: prep_min check_min help

# Show help
help:
	@echo ""
	@echo -e "Usage: make <\033[31mtarget\033[0m>"
	@echo ""
	@echo "Targets:"
	@echo -e "  \033[31mprep\033[0m         :  Assembling the system"
	@echo ""
	@echo -e "  \033[31mprep_\033[0m<step>  :  step: min, eq, md, ti. Prepare input files for step."
	@echo ""
	@echo -e "  \033[31mcheck_\033[0m<step> :  step: min, eq, md, ti, analyze. Check the logs/step.err file for any GROMACS errors."
	@echo ""
	@echo -e "  \033[31ms_\033[0m<step>     :  step: min, eq, md, ti. Check if the GROMACS run was successful."
	@echo ""
	@echo -e "  \033[31manalyze\033[0m      :  Analyze the results and produce the plots."
	@echo ""
	@echo -e "  \033[31mimg\033[0m          :  Generates all results image from pre-existing results_summary.csv files."
	@echo ""
	@echo -e "  \033[31mval\033[0m          :  Display the validation checks from the analysis log."
	@echo ""
	@echo -e "  \033[31mnew\033[0m          :  Create a new run by removing the previous input and working directory files (confirmation will be prompted)."
	@echo ""
	@echo -e "  \033[31mclean\033[0m        :  Clean up all backup files inside the workPath (confirmation will be prompted)."
	@echo ""
	@echo -e "  \033[31mhelp\033[0m         :  Display this help message."


# assembly system
prep:
	@rm -f logs/prep* logs/*prep.log
	@echo ">>> Preparing input files for assembly system..."
	@sbatch NEMAT/run_files/prep.sh

# Check if there are any errors in the log
check_prep:
	@echo ">>> Checking for errors in assembly log..."
	@bash NEMAT/check.sh prep
	@cat logs/checklist.txt

# Prepare minimization files
prep_min:
	@rm -f logs/min* logs/*min.log
	@echo ">>> Preparing minimization..."
	@sbatch NEMAT/run_files/prep_min.sh

# Check if there are any errors in the log
check_min:
	@echo ">>> Checking for errors in minimization log..."
	@bash NEMAT/check.sh min


# Prepare equilibration files
prep_eq:
	@rm -f logs/eq* logs/*eq.log
	@echo ">>> Preparing equilibration..."
	@sbatch NEMAT/run_files/prep_eq.sh

# Check if there are any errors in the log
check_eq:
	@echo ">>> Checking for errors in equilibration log..."
	@bash NEMAT/check.sh eq


# Prepare production files
prep_md:
	@rm -f logs/md* logs/*md.log
	@echo ">>> Preparing production..."
	@sbatch NEMAT/run_files/prep_md.sh

# Check if there are any errors in the log
check_md:
	@echo ">>> Checking for errors in production log..."
	@bash NEMAT/check.sh md



# Prepare transition files
prep_ti:
	@rm -f logs/ti* logs/*ti.log
	@echo ">>> Preparing transition..."
	@sbatch NEMAT/run_files/prep_ti.sh

# Check if there are any errors in the log
check_ti:
	@echo ">>> Checking for errors in transition log..."
	@bash NEMAT/check.sh ti


# Analyze the results
wp := $(shell grep "workPath:" input.yaml | sed -E "s/.*workPath:[[:space:]]*'([^']+)'.*/\1/")
analyze:
	@echo ">>> Analyzing results..."
	@sbatch NEMAT/run_files/analyze.sh $(wp)

check_analyze:
	@echo ">>> Checking for errors in analysis log..."
	@bash NEMAT/check.sh analysis

img:
	@echo ">>> Generating image from pre-existing results_summary.csv..."
	@python NEMAT/file_gestor.py --step img

val:
	@echo ">>> Validating the overlap (good if >= 0.2)..."
	@python utils/overlap.py --wp $(wp)

s_min:
	@echo ">>> Checking for successful jobs in minimization..."
	@bash utils/checkSuccessfullJobs.sh em

s_eq:
	@echo ">>> Checking for successful jobs in equilibration..."
	@bash utils/checkSuccessfullJobs.sh eq

s_md:
	@echo ">>> Checking for successful jobs in production..."
	@bash utils/checkSuccessfullJobs.sh md

s_ti:
	@echo ">>> Checking for successful jobs in transition..."
	@bash utils/checkSuccessfullJobs.sh transitions

input := $(shell find . -type d -exec test -d "{}/mdppath" -a -d "{}/proteins" -a -d "{}/membrane" -a -d "{}/ligands" \; -print | tail -n 1)
new:
	@bash utils/new_run.sh $(input) $(wp)

clean:
	@bash utils/clean_backups.sh