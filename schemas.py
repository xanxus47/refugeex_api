from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class EvacueeBase(BaseModel):
    profile_id: str
    full_name: str
    age: Optional[int] = None
    sex: Optional[str] = None
    barangay: Optional[str] = None
    evacuation_center_id: str
    evacuation_center_name: str
    proof_image: Optional[str] = None
    household: Optional[str] = None
    head_of_family: Optional[str] = None
    host_address: Optional[str] = None
    center_barangay: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    # Vulnerable sectors
    is_4p: Optional[bool] = False
    is_4ps: Optional[bool] = False
    is_pregnant: Optional[bool] = False
    is_lactating: Optional[bool] = False
    is_child_headed: Optional[bool] = False
    is_single_headed: Optional[bool] = False
    is_solo_parent: Optional[bool] = False
    is_pwd: Optional[bool] = False
    is_ip: Optional[bool] = False
    is_outside_ec: Optional[bool] = False
    is_lgbt: Optional[bool] = False


class EvacueeCheckIn(EvacueeBase):
    """Used for POST /evacuee (check in)"""
    pass


class EvacueeResponse(EvacueeBase):
    id: int
    is_checked_in: Optional[bool] = True
    check_in_time: Optional[datetime] = None
    check_out_time: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CheckOutResponse(BaseModel):
    id: int
    profile_id: str
    full_name: str
    check_out_time: datetime
    is_checked_in: bool
    message: str


class SummaryResponse(BaseModel):
    total_checked_in: int
    total_checked_out: int
    total_all_time: int
    by_barangay: list
    by_evacuation_center: list
    vulnerable_sectors: dict
