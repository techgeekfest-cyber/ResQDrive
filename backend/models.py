"""Pydantic request/response models for the ResQDrive API."""
from typing import List, Optional

from pydantic import BaseModel, Field, ConfigDict


class ObservationCreate(BaseModel):
    model_config = ConfigDict(extra="ignore")
    vehicle_id: Optional[str] = None
    hazard_type: str
    latitude: float
    longitude: float
    confidence: Optional[float] = None
    severity: Optional[str] = None
    sensor_type: str = "CAMERA"
    sensor_quality: float = 1.0
    description: Optional[str] = None
    source: str = "SENSOR"  # SENSOR | CITIZEN


class CitizenReport(BaseModel):
    model_config = ConfigDict(extra="ignore")
    hazard_type: str
    latitude: float
    longitude: float
    severity: Optional[str] = "MODERATE"
    description: Optional[str] = None
    reporter_name: Optional[str] = "Anonymous Citizen"


class RoutePlanRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")
    start: str
    destination: str


class SimulationStartRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")
    scenario: str = "CYCLONE_FLOOD"
    speed: int = 2


class SimulationSpeedRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")
    speed: int = 2


class InjectRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")
    inject_type: str  # FLOOD, LANDSLIDE, ROAD_BLOCKAGE, FALLEN_TREE, POTHOLE,
                      # CONFLICTING, ROAD_CLEAR
    road_segment_id: Optional[str] = None
    incident_id: Optional[str] = None


class ResponseActionRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")
    note: Optional[str] = None
    operator: Optional[str] = "Operator"
