pyinstaller "./src/sortPDFs.py" --noconfirm --clean --onefile --noconsole --name "Sort PDFs.exe"

Copy-Item "./src/config.toml" "./dist/config.toml"
Remove-Item "./*.spec" -Recurse -Force
Remove-Item "./build" -Recurse -Force