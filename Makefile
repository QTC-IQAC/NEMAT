.PHONY: prep_min check_min help

# Show help
help:
	@echo ""
	@echo -e "Usage: make <\033[31mtarget\033[0m>"
	@echo ""
	@echo "Targets:"
	@echo -e "  \033[31mprep\033[0m         :  Assembling the system"
	@echo ""
	@echo -e "  \033[31mcheck_prep\033[0m   :  Check the logs/prep.err file for any errors"
	@echo ""
	@echo -e "  \033[31mprep_min\033[0m     :  Prepare input files for energy minimization for every system"
	@echo ""
	@echo -e "  \033[31mcheck_min\033[0m    :  Check the logs/min.err file for any errors"
	@echo ""
	@echo -e "  \033[31mprep_eq\033[0m      :  Prepare input files for equilibration for every system"
	@echo ""
	@echo -e "  \033[31mcheck_eq\033[0m     :  Check the logs/eq.err file for any errors"
	@echo ""
	@echo -e "  \033[31mprep_md\033[0m      :  Prepare input files for production for every system"
	@echo ""
	@echo -e "  \033[31mcheck_md\033[0m     :  Check the logs/md.err file for any errors"
	@echo ""
	@echo -e "  \033[31mprep_ti\033[0m      :  Prepare input files for transition for every system"
	@echo ""
	@echo -e "  \033[31mcheck_ti\033[0m     :  Check the logs/ti.err file for any errors"
	@echo ""
	@echo -e "  \033[31manalyze\033[0m      :  Analyze the results and produce the plots. USAGE: make analyze wp='work_path'"
	@echo ""
	@echo -e "\033[31mcheck_analyze\033[0m  :  Check the logs/analyze.err file for any errors"
	@echo ""
	@echo -e "  \033[31mimg\033[0m          :  Generates all results image from pre-existing results_summary.csv files."
	@echo ""
	@echo -e "  \033[31mhelp\033[0m         :  Display this help message"


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