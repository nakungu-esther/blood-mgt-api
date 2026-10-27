# AfriBlood AI (prototype)

Independent FastAPI service. All inputs must be synthetic for development.

## Windows PowerShell

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Visit http://127.0.0.1:8000/docs for interactive endpoint documentation.

## API

- GET /health
- POST /api/v1/forecast
- POST /api/v1/shortage
- POST /api/v1/redistribution

Forecast uses a weighted recent-average baseline, **not trained machine learning**. Forecast bands are illustrative, not calibrated confidence intervals. Redistribution is an arithmetic stock-count suggestion and does not assess clinical compatibility, cold-chain, travel time, screening or release eligibility.

Do not expose this unauthenticated service publicly or process real donor/patient information. A future NestJS integration should validate users, facilities, data provenance and clinical governance before forwarding sanitized aggregates.
