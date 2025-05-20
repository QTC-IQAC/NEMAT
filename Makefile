.PHONY: prep_min check_min help

# Show help
help:
	@echo "Usage: make <target>"
	@echo ""
	@echo "Targets:"
	@echo "  prep       :  Assembling the system"
	@echo "  check_prep :  Check the logs/prep.err file for any errors"
	@echo "  prep_min   :  Prepare input files for energy minimization for every system"
	@echo "  check_min  :  Check the logs/min.err file for any errors"
	@echo "  prep_eq    :  Prepare input files for equilibration for every system"
	@echo "  check_eq   :  Check the logs/eq.err file for any errors"
	@echo "  prep_md    :  Prepare input files for production for every system"
	@echo "  check_md   :  Check the logs/md.err file for any errors"
	@echo "  help       :  Display this help message"


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

