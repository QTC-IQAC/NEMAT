.PHONY: prep_min check_min help
PYTHON=$(shell which python)
SRC=$(NMT_HOME)/src
WP=$(shell grep "workPath:" $(shell pwd)/input.yaml | sed -E "s/.*workPath:[[:space:]]*'([^']+)'.*/\1/")
INPUT=$(shell grep "inputDirName:" $(shell pwd)/input.yaml | sed -E "s/.*inputDirName:[[:space:]]*'([^']+)'.*/\1/")


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


# Prepare equilibration files
prep_eq:
	@rm -f logs/eq* logs/*eq.log
	@echo ">>> Preparing equilibration..."
	@sbatch $(SRC)/NEMAT/run_files/prep_eq.sh

# Check if there are any errors in the log
check_eq:
	@echo ">>> Checking for errors in equilibration log..."
	@bash $(SRC)/NEMAT/check.sh eq


# Prepare production files
prep_md:
	@rm -f logs/md* logs/*md.log
	@echo ">>> Preparing production..."
	@sbatch $(SRC)/NEMAT/run_files/prep_md.sh

# Check if there are any errors in the log
check_md:
	@echo ">>> Checking for errors in production log..."
	@bash $(SRC)/NEMAT/check.sh md



# Prepare transition files
prep_ti:
	@rm -f logs/ti* logs/*ti.log
	@echo ">>> Preparing transition..."
	@sbatch $(SRC)/NEMAT/run_files/prep_ti.sh

# Check if there are any errors in the log
check_ti:
	@echo ">>> Checking for errors in transition log..."
	@bash $(SRC)/NEMAT/check.sh ti


# Analyze the results
analyze:
	@echo ">>> Analyzing results from $(WP)..."
	@sbatch $(SRC)/NEMAT/run_files/analyze.sh $(WP)

check_analyze:
	@echo ">>> Checking for errors in analysis log..."
	@bash $(SRC)/NEMAT/check.sh analysis

img:
	@echo ">>> Generating image from pre-existing results_summary.csv..."
	@$(PYTHON) $(SRC)/NEMAT/file_gestor.py --step img

val:
	@echo ">>> Validating the overlap (good if >= 0.2)..."
	@$(PYTHON) $(SRC)/utils/overlap.py --WP $(WP)

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
	@read -p "Enter new destination path: " dest; \
	read -p "Enter level (eq, md or all): " level; \
	bash $(SRC)/utils/copy_new.sh $(WP) $$dest $$level

update:
	@echo ">>> Updating NEMAT parameters to match input.yaml..."
	@sbatch $(SRC)/NEMAT/run_files/update_params.sh
	@make check_prep

start:
	@bash $(SRC)/utils/start.sh
# 	@echo "workPath is set to: $(WP)"
# 	@echo "Input directory is set to: $(INPUT)"



