# Initialize Database
$rootPath = Split-Path -Parent $MyInvocation.MyCommand.Path
cd "$rootPath\services\link_management"
& "$rootPath\.venv\Scripts\python.exe" init_db.py
