from datetime import date
import uuid

from pydantic import BaseModel as BaseSchema, ConfigDict, Field, field_validator
from enum import Enum

class StatutIntervention(str, Enum):
    planned = "planifiée"
    confirmed = "confirmée"
    cancelled = "annulée"

class InterventionCreate(BaseSchema):
    model_config = ConfigDict(str_strip_whitespace=True)

    start_date: date
    location: str = Field(min_length=2, max_length=80)
    places: int = Field(ge=1, le=30)
    statut: StatutIntervention = StatutIntervention.planned

    @field_validator("start_date")
    @classmethod
    def in_the_future(cls, valeur: date) -> date:
        if valeur <= date.today():
            raise ValueError("la date de début doit être postérieure à aujourd'hui")
        return valeur


class InterventionFormation(InterventionCreate):
    id: uuid.UUID
    formation_id: uuid.UUID