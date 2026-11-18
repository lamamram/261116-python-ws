import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

# arbitraire:   renommage de BaseModel en BaseSchema car Model fait référence à la classe générique en ORM !
from pydantic import BaseModel as BaseSchema, ConfigDict, Field


class Level(str, Enum):
    beginner = "initiation"
    medium = "intermediaire"
    advanced = "avancé"


class FormationSchema(BaseSchema):
    # ------------> config générale d'une schéma: str_strip_whitespace=True permet de supprimer les espaces en début et fin de chaîne
    model_config = ConfigDict(str_strip_whitespace=True)
    # -------------------------------------------------> documentation d'openapi
    code: str = Field(pattern=r"^[A-Z]{3}\d{6}-[A-Z]$", examples=["PYT100614-F"])
    titre: str = Field(min_length=3, max_length=120)
    # description: str | None = Field(default=None, max_length=2000)
    description: Optional[str] = Field(default=None, max_length=2000)
    duration: int = Field(ge=1, le=10)
    level: Level

class FormationCreate(FormationSchema):
    ...

class FormationUpdate(BaseSchema):
    # ---------------------------------------------------> interdit les champs supplémentaires non définis dans le schéma
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    titre: str | None = Field(default=None, min_length=3, max_length=120)
    description: str | None = Field(default=None, max_length=2000)
    duration: int | None = Field(default=None, ge=1, le=10)
    level: Level | None = None
