@echo off
REM TOSCA Unused Files Cleanup Script (Windows) - CORRECTED VERSION
REM Created: 2025-11-02
REM Purpose: Remove duplicate and unused files identified in code review
REM Estimated space savings: ~180 KB (revised after analysis)
REM
REM IMPORTANT: Xeryon.py in actuator_module root is USED by production code!
REM Only delete files with (1) suffix and duplicate test directories.

echo ========================================
echo TOSCA Unused Files Cleanup Script
echo CORRECTED VERSION - Safe Deletions Only
echo ========================================
echo.

cd /d "%~dp0.."
echo Project root: %CD%
echo.

set DELETED=0

echo ========================================
echo 1. DUPLICATE TEST DIRECTORIES
echo ========================================
echo.

REM 1. Delete duplicate VmbPy Tests/ directory (capital T)
set "FILE1=components\camera_module\tests\vmbpy_unit_tests\Tests"
if exist "%FILE1%" (
    echo [1/4] Deleting: Duplicate VmbPy Tests/ directory (284 KB)
    echo   Path: %FILE1%
    echo   Reason: Exact duplicate of lowercase 'tests/' directory
    choice /C YN /M "Confirm deletion"
    if errorlevel 2 (
        echo   Skipped
    ) else (
        rmdir /s /q "%FILE1%"
        if not exist "%FILE1%" (
            echo   SUCCESS: Deleted successfully
            set /a DELETED+=1
        ) else (
            echo   ERROR: Failed to delete
        )
    )
    echo.
) else (
    echo [1/4] Already gone: %FILE1%
    echo.
)

echo ========================================
echo 2. DOWNLOAD DUPLICATES (files with ^(1^) suffix)
echo ========================================
echo.

REM 2. Delete Xeryon(1).py - download duplicate
set "FILE2=components\actuator_module\manufacturer_docs\xeryon_library\Xeryon(1).py"
if exist "%FILE2%" (
    echo [2/4] Deleting: Xeryon^(1^).py (58 KB)
    echo   Path: %FILE2%
    echo   Reason: Download duplicate - Xeryon.py already exists
    choice /C YN /M "Confirm deletion"
    if errorlevel 2 (
        echo   Skipped
    ) else (
        del /q "%FILE2%"
        if not exist "%FILE2%" (
            echo   SUCCESS: Deleted successfully
            set /a DELETED+=1
        ) else (
            echo   ERROR: Failed to delete
        )
    )
    echo.
) else (
    echo [2/4] Already gone: %FILE2%
    echo.
)

REM 3. Delete python example(1).py - download duplicate
set "FILE3=components\actuator_module\manufacturer_docs\xeryon_library\python example(1).py"
if exist "%FILE3%" (
    echo [3/4] Deleting: python example^(1^).py
    echo   Path: %FILE3%
    echo   Reason: Download duplicate
    choice /C YN /M "Confirm deletion"
    if errorlevel 2 (
        echo   Skipped
    ) else (
        del /q "%FILE3%"
        if not exist "%FILE3%" (
            echo   SUCCESS: Deleted successfully
            set /a DELETED+=1
        ) else (
            echo   ERROR: Failed to delete
        )
    )
    echo.
) else (
    echo [3/4] Already gone: %FILE3%
    echo.
)

echo ========================================
echo 3. ARCHIVED OBSOLETE FILES
echo ========================================
echo.

REM 4. Delete archived Python script (already archived, no longer needed)
set "FILE4=archive\2025-10-archive\presubmit-old\apply_camera_fix.py"
if exist "%FILE4%" (
    echo [4/4] Deleting: Archived apply_camera_fix.py
    echo   Path: %FILE4%
    echo   Reason: Old script in archive folder, no longer needed
    choice /C YN /M "Confirm deletion"
    if errorlevel 2 (
        echo   Skipped
    ) else (
        del /q "%FILE4%"
        if not exist "%FILE4%" (
            echo   SUCCESS: Deleted successfully
            set /a DELETED+=1
        ) else (
            echo   ERROR: Failed to delete
        )
    )
    echo.
) else (
    echo [4/4] Already gone: %FILE4%
    echo.
)

echo ========================================
echo CLEANUP SUMMARY
echo ========================================
echo.
echo Files deleted: %DELETED%/4
echo Estimated space saved: ~180 KB
echo.

echo ========================================
echo IMPORTANT: Files KEPT (Not Duplicates)
echo ========================================
echo.
echo components\actuator_module\Xeryon.py
echo   - USED by src\hardware\actuator_controller.py
echo   - DO NOT DELETE
echo.
echo components\actuator_module\manufacturer_docs\xeryon_library\Xeryon.py
echo   - Vendor reference copy
echo   - DO NOT DELETE
echo.

echo ========================================
echo NEXT STEPS
echo ========================================
echo.
echo 1. Verify tests pass: pytest tests\ -v
echo 2. Check actuator works: python src\main.py
echo 3. Document in WORK_LOG.md
echo.

pause
