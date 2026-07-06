@echo off
setlocal
cd /d "%~dp0"

title Mechanical Technical Document Evaluation Harness Demo

set "ROOT=%~dp0"
set "PYTHON=%ROOT%.venv\Scripts\python.exe"
set "OUTPUT=%ROOT%demo_output"
set "RUNS=%OUTPUT%\runs"
set "REPORT=%OUTPUT%\portfolio-demo-report.md"

echo ============================================================
echo  MECHANICAL TECHNICAL DOCUMENT EVALUATION HARNESS
echo  Portfolio Demonstration
echo ============================================================
echo.

if not exist "%PYTHON%" (
    echo ERROR: The project virtual environment was not found.
    echo Expected:
    echo %PYTHON%
    echo.
    pause
    exit /b 1
)

if not exist "%OUTPUT%" mkdir "%OUTPUT%"

echo Running one valid and one defective engineering artifact...
echo.

"%PYTHON%" "%ROOT%scripts\run_portfolio_demo.py" --runs-dir "%RUNS%" --report-path "%REPORT%"

if errorlevel 1 (
    echo.
    echo ============================================================
    echo  DEMONSTRATION FAILED
    echo ============================================================
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo  DEMONSTRATION COMPLETE - 2/2 SCENARIOS VERIFIED
echo ============================================================
echo.
echo Readable report:
echo %REPORT%
echo.
echo Generated evidence:
echo %OUTPUT%
echo.

start "" "%REPORT%"
start "" explorer "%OUTPUT%"

pause
