@echo off
REM ── 1) Activate the Conda environment ─────────────────────────────────────────
CALL conda activate stp
IF ERRORLEVEL 1 (
  ECHO ❌ Failed to activate stp. Make sure it exists.
  PAUSE
  EXIT /B 1
)