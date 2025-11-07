@echo off
REM TOSCA Architecture Diagram Generation Script (Windows)
REM Generates PNG and SVG images from PlantUML sources

setlocal enabledelayedexpansion

echo =========================================
echo TOSCA Architecture Diagram Generator
echo =========================================
echo.

REM Check for PlantUML JAR
set PLANTUML_JAR=plantuml.jar

if not exist "%PLANTUML_JAR%" (
    echo ERROR: plantuml.jar not found
    echo.
    echo Please download PlantUML JAR manually:
    echo   1. Visit: https://plantuml.com/download
    echo   2. Download plantuml.jar
    echo   3. Place it in this directory: %CD%
    echo.
    pause
    exit /b 1
)

REM Check for Java
java -version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Java not found
    echo.
    echo Please install Java Runtime Environment ^(JRE^) 8+
    echo Download from: https://www.oracle.com/java/technologies/downloads/
    echo.
    pause
    exit /b 1
)

REM Create output directories
if not exist "output\png" mkdir output\png
if not exist "output\svg" mkdir output\svg

echo Generating diagrams...
echo.

REM Count .puml files
set PUML_COUNT=0
for %%f in (*.puml) do set /a PUML_COUNT+=1
echo Found %PUML_COUNT% PlantUML source files
echo.

REM Generate PNG diagrams
echo [1/2] Generating PNG images...
java -jar "%PLANTUML_JAR%" -tpng *.puml -o output\png
echo   OK PNG images generated in output\png\
echo.

REM Generate SVG diagrams
echo [2/2] Generating SVG images...
java -jar "%PLANTUML_JAR%" -tsvg *.puml -o output\svg
echo   OK SVG images generated in output\svg\
echo.

REM Count generated files
set PNG_COUNT=0
set SVG_COUNT=0
for %%f in (output\png\*.png) do set /a PNG_COUNT+=1
for %%f in (output\svg\*.svg) do set /a SVG_COUNT+=1

echo =========================================
echo Diagram generation complete!
echo =========================================
echo.
echo PNG images: %PNG_COUNT% files
echo SVG images: %SVG_COUNT% files
echo.
echo To view diagrams:
echo   PNG: explorer output\png
echo   SVG: explorer output\svg
echo.
pause
