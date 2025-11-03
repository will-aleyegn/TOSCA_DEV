@echo off
REM TOSCA Unused Files Cleanup Script (Windows)
REM Created: 2025-11-02
REM Purpose: Remove duplicate and unused files identified in code review
REM Estimated space savings: ~400 KB

echo ========================================
echo TOSCA Unused Files Cleanup Script
echo ========================================
echo.

cd /d "%~dp0.."
echo Project root: %CD%
echo.

echo ========================================
echo 1. DUPLICATE FILES
echo ========================================
echo.

REM 1. Delete duplicate VmbPy Tests/ directory
set "FILE1=components\camera_module\tests\vmbpy_unit_tests\Tests"
if exist "%FILE1%" (
    echo [1/5] Deleting: Duplicate VmbPy Tests/ directory
    echo   Path: %FILE1%
    choice /C YN /M "Confirm deletion"
    if errorlevel 2 (
        echo   Skipped
    ) else (
        rmdir /s /q "%FILE1%"
        echo   Deleted successfully
    )
    echo.
) else (
    echo [1/5] Not found: %FILE1%
    echo.
)

REM 2. Delete duplicate Xeryon.py
set "FILE2=components\actuator_module\Xeryon.py"
if exist "%FILE2%" (
    echo [2/5] Deleting: Duplicate Xeryon.py
    echo   Path: %FILE2%
    choice /C YN /M "Confirm deletion"
    if errorlevel 2 (
        echo   Skipped
    ) else (
        del /q "%FILE2%"
        echo   Deleted successfully
    )
    echo.
) else (
    echo [2/5] Not found: %FILE2%
    echo.
)

REM 3. Delete Xeryon(1).py
set "FILE3=components\actuator_module\manufacturer_docs\xeryon_library\Xeryon(1).py"
if exist "%FILE3%" (
    echo [3/5] Deleting: Xeryon(1).py duplicate
    echo   Path: %FILE3%
    choice /C YN /M "Confirm deletion"
    if errorlevel 2 (
        echo   Skipped
    ) else (
        del /q "%FILE3%"
        echo   Deleted successfully
    )
    echo.
) else (
    echo [3/5] Not found: %FILE3%
    echo.
)

REM 4. Delete python example(1).py
set "FILE4=components\actuator_module\manufacturer_docs\xeryon_library\python example(1).py"
if exist "%FILE4%" (
    echo [4/5] Deleting: python example(1).py duplicate
    echo   Path: %FILE4%
    choice /C YN /M "Confirm deletion"
    if errorlevel 2 (
        echo   Skipped
    ) else (
        del /q "%FILE4%"
        echo   Deleted successfully
    )
    echo.
) else (
    echo [4/5] Not found: %FILE4%
    echo.
)

echo ========================================
echo 2. ARCHIVED FILES
echo ========================================
echo.

REM 5. Delete archived script
set "FILE5=archive\2025-10-archive\presubmit-old\apply_camera_fix.py"
if exist "%FILE5%" (
    echo [5/5] Deleting: Archived apply_camera_fix.py
    echo   Path: %FILE5%
    choice /C YN /M "Confirm deletion"
    if errorlevel 2 (
        echo   Skipped
    ) else (
        del /q "%FILE5%"
        echo   Deleted successfully
    )
    echo.
) else (
    echo [5/5] Not found: %FILE5%
    echo.
)

echo ========================================
echo CLEANUP COMPLETE
echo ========================================
echo.
echo Next steps:
echo 1. Verify imports: findstr /s /i "import.*Xeryon" src\*.py
echo 2. Run tests: pytest tests\ -v
echo 3. Check functionality: python src\main.py
echo.

pause
