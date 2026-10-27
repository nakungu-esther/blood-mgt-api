from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .models import ForecastRequest, ShortageRequest, RedistributionRequest
from .engine import forecast, shortage, redistribution

app = FastAPI(title='AfriBlood AI - Prototype',version='0.1.0',
              description='Synthetic-data decision-support prototype. Not for clinical use.')
# No browser origins enabled: backend-to-backend integration is intended.
app.add_middleware(CORSMiddleware,allow_origins=[],allow_methods=['GET','POST'],allow_headers=['Content-Type'])

@app.get('/health')
def health():
    return {'status':'ok','service':'afriblood-ai','mode':'prototype'}

@app.post('/api/v1/forecast')
def forecast_route(payload:ForecastRequest):
    return forecast(payload)

@app.post('/api/v1/shortage')
def shortage_route(payload:ShortageRequest):
    return shortage(payload)

@app.post('/api/v1/redistribution')
def redistribution_route(payload:RedistributionRequest):
    return redistribution(payload)
