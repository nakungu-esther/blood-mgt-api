from datetime import timedelta
from math import ceil
from .models import ForecastRequest, ShortageRequest, RedistributionRequest

DISCLAIMER = ('Prototype decision-support only; not clinical compatibility, product release, '
              'transfusion advice, or a validated supply-chain optimization model.')

def forecast(req: ForecastRequest) -> dict:
    values = [x.units for x in req.history]
    # Transparent weighted recent-average baseline, not a trained ML model.
    recent = values[-min(7,len(values)):]
    weights = list(range(1,len(recent)+1))
    daily = sum(v*w for v,w in zip(recent,weights))/sum(weights)
    # Reflect historic variability, not a statistical prediction interval.
    low_daily = max(0, daily*0.75)
    high_daily = daily*1.25
    start = req.history[-1].day
    return {
        'facility_id':req.facility_id,'blood_group':req.blood_group,
        'component':req.component,'model':'weighted_recent_average_v1',
        'forecast':[{'day':(start+timedelta(days=i)).isoformat(),
                     'predicted_units':round(daily,2),
                     'illustrative_low':round(low_daily,2),
                     'illustrative_high':round(high_daily,2)}
                    for i in range(1,req.horizon_days+1)],
        'total_predicted_units':round(daily*req.horizon_days,2),
        'note':'Illustrative bands are NOT validated confidence intervals. '+DISCLAIMER
    }

def shortage(req: ShortageRequest) -> dict:
    target = req.expected_demand_units + req.safety_stock_units
    gap = max(0,target-req.available_units)
    return {'facility_id':req.facility_id,'blood_group':req.blood_group,
            'component':req.component,'available_units':req.available_units,
            'target_units':target,'shortage_units':gap,
            'status':'SHORTAGE' if gap else 'SUFFICIENT_ON_COUNTS',
            'note':DISCLAIMER}

def redistribution(req: RedistributionRequest) -> dict:
    # Independent stock-count suggestions by exact label only; no cross-group compatibility.
    grouped = {}
    for item in req.inventory:
        grouped.setdefault((item.blood_group,item.component),[]).append(item)
    suggestions = []
    for (group,component),items in grouped.items():
        sources=[]; destinations=[]
        for item in sorted(items,key=lambda x:x.facility_id):
            target=req.demand_by_facility.get(item.facility_id,0)+req.safety_stock_units
            surplus=max(0,item.available_units-item.expiring_within_7_days-target)
            deficit=max(0,target-item.available_units)
            if surplus: sources.append([item.facility_id,surplus])
            if deficit: destinations.append([item.facility_id,deficit])
        for destination in destinations:
            for source in sources:
                if destination[1]==0: break
                if source[1]==0 or source[0]==destination[0]: continue
                amount=min(source[1],destination[1]); source[1]-=amount; destination[1]-=amount
                suggestions.append({'source_facility_id':source[0],
                                    'destination_facility_id':destination[0],
                                    'blood_group':group,'component':component,
                                    'suggested_units':amount,
                                    'status':'REVIEW_REQUIRED'})
    return {'suggestions':suggestions,'note':('No distance, cold-chain, reservation, '
            'clinical screening or crossmatching checks performed. '+DISCLAIMER)}
