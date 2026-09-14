# 4D-EPDM: Makefile for Reproducible Empirical Macroeconomics
.PHONY: all help reproduce-paper eval sim stress figures dashboard clean

PYTHON ?= python

help:
	@echo "4D-EPDM Reproduction & Research Suite"
	@echo "---------------------------------------"
	@echo "make reproduce-paper : Run entire replication pipeline (eval, sim, stress, figures)"
	@echo "make eval            : Run 19 rolling origins out-of-sample evaluation harness"
	@echo "make sim             : Run 9D capability simulation and Monte Carlo trajectories"
	@echo "make stress          : Run adversarial crisis and placebo stress-testing"
	@echo "make figures         : Generate publication-grade 300 DPI figures"
	@echo "make dashboard       : Launch interactive Streamlit capability dashboard"
	@echo "make clean           : Remove Python bytecode cache"

all: reproduce-paper

reproduce-paper:
	$(PYTHON) run_all.py --all

eval:
	$(PYTHON) run_evaluation.py

sim:
	$(PYTHON) power_dynamics_engine.py

stress:
	$(PYTHON) stress_testing.py

figures:
	$(PYTHON) generate_video_figures.py

dashboard:
	streamlit run dashboard.py

clean:
	$(PYTHON) -c "import pathlib, shutil; [shutil.rmtree(p) for p in pathlib.Path('.').rglob('__pycache__')]"
