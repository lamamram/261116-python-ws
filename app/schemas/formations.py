import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

# arbitraire:   renommage de BaseModel en BaseSchema car Model fait référence à la classe générique en ORM !
from pydantic import BaseModel as BaseSchema, ConfigDict, Field, field_validator, model_validator


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

    @field_validator("duration")
    @classmethod
    def odd_duration(cls, value: int):
        """
        un validateur de champs est évalué avec son schéma
        
        peut transformer la valeur du champs en paramètre et la retourner: formatter

        peut bloquer la validation pour des considérations avancées, métier
        """
        if not value % 2:
            raise ValueError(f"{value} doit être impair !!")
        return value

    @model_validator(mode="after")
    def level_matching_duration(self):
        """
        un validateur sur plusieurs champs, qui nécessite l'instance du schéma
        """
        matches = {
            "initiation": 1,
            "intermédiaire": 3,
            "avancé": 5
        }
        if self.duration <= matches[self.level]:
            raise ValueError(f"une formation de niveau {self.level} demande au moins {matches[self.level]} j")
        return self

class FormationCreate(FormationSchema):
    ...

class FormationUpdate(BaseSchema):
    # ---------------------------------------------------> interdit les champs supplémentaires non définis dans le schéma
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    titre: str | None = Field(default=None, min_length=3, max_length=120)
    description: str | None = Field(default=None, max_length=2000)
    duration: int | None = Field(default=None, ge=1, le=10)
    level: Level | None = None
