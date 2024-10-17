steps:
1. python version need 3.11
2. create virtual env
    python3.11 -m venv venv
3. source venv/bin/activate - mac
   venv\Scripts\Activate.ps1 - windows in powershell
4. pip install -r requirements.txt
5. uvicorn app:app --reload --port 9000

