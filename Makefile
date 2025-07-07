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
	@echo -e "  \033[31mhelp\033[0m         :  Display this help message."


# assembly system
prep:
	@echo ">>> Preparing input files for assembly system..."
	@sbatch NEMAT/run_files/prep.sh

# Check if there are any errors in the log
check_prep:
	@echo ">>> Checking for errors in assembly log..."
	@bash NEMAT/check.sh prep


# Prepare minimization files
prep_min:
	@echo ">>> Preparing minimization..."
	@sbatch NEMAT/run_files/prep_min.sh

# Check if there are any errors in the log
check_min:
	@echo ">>> Checking for errors in minimization log..."
	@bash NEMAT/check.sh min


# Prepare equilibration files
prep_eq:
	@echo ">>> Preparing equilibration..."
	@sbatch NEMAT/run_files/prep_eq.sh

# Check if there are any errors in the log
check_eq:
	@echo ">>> Checking for errors in equilibration log..."
	@bash NEMAT/check.sh eq


# Prepare production files
prep_md:
	@echo ">>> Preparing production..."
	@sbatch NEMAT/run_files/prep_md.sh

# Check if there are any errors in the log
check_md:
	@echo ">>> Checking for errors in production log..."
	@bash NEMAT/check.sh md



# Prepare transition files
prep_ti:
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
	@echo ">>> Validating the input files..."
	@echo ''
	@grep -E "^--> edge_" logs/analysis.log
	@echo ""
	@awk '/-+VALIDATION-+/{flag=1; print; next} /-{3,}/{if(flag){print; exit}} flag' logs/analysis.log
	@echo ""

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
	@bash utils/checkSuccessfullJobs.sh ti
