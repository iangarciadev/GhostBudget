@echo off
echo === GhostBudget Build ===
echo.

echo Instalando PyInstaller...
pip install pyinstaller --quiet
if errorlevel 1 (
    echo ERRO: Falhou ao instalar PyInstaller. Verifique se o Python esta no PATH.
    pause
    exit /b 1
)

echo Compilando o app...
pyinstaller ghostbudget.spec --clean --noconfirm
if errorlevel 1 (
    echo ERRO: Build falhou. Veja os erros acima.
    pause
    exit /b 1
)

echo.
echo ===================================
echo  Build concluido com sucesso!
echo  Executavel: dist\GhostBudget\GhostBudget.exe
echo
echo  Para distribuir: compacte a pasta dist\GhostBudget\
echo  e envie para o usuario.
echo ===================================
pause
