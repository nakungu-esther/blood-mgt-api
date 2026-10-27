from datetime import date
from typing import Literal
from pydantic import BaseModel, Field, model_validator

BloodGroup = Literal['A_POS','A_NEG','B_POS','B_NEG','AB_POS','AB_NEG','O_POS','O_NEG']
Component = Literal['WHOLE_BLOOD','RED_CELLS','PLASMA','PLATELETS']

class DemandObservation(BaseModel):
    day: date
    units: int = Field(ge=0, le=100000)

class ForecastRequest(BaseModel):
    facility_id: str = Field(min_length=1, max_length=100)
    blood_group: BloodGroup
    component: Component
    history: list[DemandObservation] = Field(min_length=3, max_length=730)
    horizon_days: int = Field(default=7, ge=1, le=30)

    @model_validator(mode='after')
    def check_dates(self):
        days = [x.day for x in self.history]
        if len(set(days)) != len(days):
            raise ValueError('Duplicate history dates')
        if days != sorted(days):
            raise ValueError('History must be sorted by date')
        if any((b-a).days != 1 for a,b in zip(days,days[1:])):
            raise ValueError('History must have consecutive daily dates, including zero-demand days')
        if days[-1] > date.today():
            raise ValueError('Future demand observations are not allowed')
        return self

class InventoryItem(BaseModel):
    facility_id: str = Field(min_length=1)
    blood_group: BloodGroup
    component: Component
    available_units: int = Field(ge=0)
    expiring_within_7_days: int = Field(default=0, ge=0)
    @model_validator(mode='after')
    def check_expiring(self):
        if self.expiring_within_7_days > self.available_units:
            raise ValueError('Expiring units cannot exceed available units')
        return self

class ShortageRequest(BaseModel):
    facility_id: str = Field(min_length=1)
    blood_group: BloodGroup
    component: Component
    available_units: int = Field(ge=0)
    expected_demand_units: int = Field(ge=0)
    safety_stock_units: int = Field(default=0, ge=0)

class RedistributionRequest(BaseModel):
    inventory: list[InventoryItem] = Field(min_length=2, max_length=1000)
    demand_by_facility: dict[str,int] = Field(default_factory=dict)
    safety_stock_units: int = Field(default=2, ge=0)

    @model_validator(mode='after')
    def check_inventory(self):
        keys = [(i.facility_id,i.blood_group,i.component) for i in self.inventory]
        if len(keys) != len(set(keys)):
            raise ValueError('Duplicate facility/group/component inventory rows')
        if any(v < 0 for v in self.demand_by_facility.values()):
            raise ValueError('Demand cannot be negative')
        return self
