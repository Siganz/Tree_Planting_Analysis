@echo off
REM ── 1) Activate the Conda environment ─────────────────────────────────────────
CALL conda activate planting_env
IF ERRORLEVEL 1 (
  ECHO ❌ Failed to activate planting_env. Make sure it exists.
  PAUSE
  EXIT /B 1
)

REM ── 2) Run script #1: Download data ─────────────────────────────────────────────
ECHO. & ECHO ⏳ Running 1_download_data.py…
python scripts\1_download_data.py
IF ERRORLEVEL 1 (
  ECHO ❌ 1_download_data.py failed. Check the output above.
  PAUSE
  EXIT /B 1
)

REM ── 3) Run script #2: Political boundary processing ─────────────────────────────
ECHO. & ECHO ⏳ Running 2_political_boundary.py…
python scripts\2_fields_inventory.py
IF ERRORLEVEL 1 (
  ECHO ❌ 2_political_boundary.py failed. Check the output above.
  PAUSE
  EXIT /B 1
)

REM ── 5) All done ────────────────────────────────────────────────────────────────
ECHO. & ECHO ✅ All scripts completed successfully.
PAUSE
