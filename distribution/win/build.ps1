pyinstaller --clean --noconfirm installed.spec
pyinstaller --clean --noconfirm portable.spec

iscc installer.iss

cp .\dist\Vaultea.exe .\Output\

Remove-Item './build' -Recurse
Remove-Item './dist' -Recurse
