from datetime import date, timedelta
from fastapi.testclient import TestClient
from app.main import app

client=TestClient(app)

def test_health():
    response=client.get('/health')
    assert response.status_code==200
    assert response.json()['status']=='ok'

def test_forecast():
    start=date.today()-timedelta(days=3)
    payload={'facility_id':'demo-1','blood_group':'O_POS','component':'RED_CELLS',
             'history':[{'day':(start+timedelta(days=i)).isoformat(),'units':i+1} for i in range(3)],
             'horizon_days':7}
    response=client.post('/api/v1/forecast',json=payload)
    assert response.status_code==200,response.text
    assert len(response.json()['forecast'])==7

def test_duplicate_dates_rejected():
    day=(date.today()-timedelta(days=1)).isoformat()
    payload={'facility_id':'demo-1','blood_group':'O_POS','component':'RED_CELLS',
             'history':[{'day':day,'units':2}]*3}
    assert client.post('/api/v1/forecast',json=payload).status_code==422

def test_shortage():
    payload={'facility_id':'demo-1','blood_group':'O_POS','component':'RED_CELLS',
             'available_units':2,'expected_demand_units':8,'safety_stock_units':2}
    assert client.post('/api/v1/shortage',json=payload).json()['shortage_units']==8

def test_redistribution():
    payload={'inventory':[{'facility_id':'bank-a','blood_group':'O_POS','component':'RED_CELLS','available_units':20},
                          {'facility_id':'bank-b','blood_group':'O_POS','component':'RED_CELLS','available_units':1}],
             'demand_by_facility':{'bank-a':5,'bank-b':8},'safety_stock_units':2}
    response=client.post('/api/v1/redistribution',json=payload)
    assert response.status_code==200,response.text
    assert response.json()['suggestions'][0]['suggested_units']==9
