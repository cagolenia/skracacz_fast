# Run Analytics Worker
cd services/analytics
$env:PYTHONPATH = "$PWD"
..\..\\.venv\Scripts\python.exe src/worker.py
