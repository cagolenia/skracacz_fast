# Run Link Management Service
cd C:\Users\Cezary\Documents\My\skracacz_fast\services\link_management
$env:PYTHONPATH = "$PWD"
& "C:\Users\Cezary\Documents\My\skracacz_fast\.venv\Scripts\python.exe" -m uvicorn src.main:app --reload --port 8001 --host 127.0.0.1
