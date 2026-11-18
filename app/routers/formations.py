# app/routers/formations.py
from fastapi import APIRouter, Path, Query, HTTPException
from typing import Annotated, Literal
import uuid

# objet router à connecter à l'app !
router = APIRouter(prefix="/formations", tags=["formations"])

# version entier
FORMATIONS_INT = [
    {"code": "PYT100614-F", "titre": "Python Avancé : Web Services", "level": "advanced", "duration": 3, "description": "Formation avancée sur les Web Services en Python"},
    {"code": "JAV100614-B", "titre": "Java Avancé : Bases", "level": "advanced", "duration": 5, "description": "Formation avancée sur les bases en Java"},
    {"code": "DOK100614-C", "titre": "Docker initiation : Conteneurs", "level": "beginner", "duration": 2, "description": "Formation d'initiation à Docker et aux conteneurs"},
]

FORMATIONS_SLUG = {
    "python-avance-web-services": {"code": "PYT100614-F", "titre": "Python Avancé : Web Services", "level": "advanced", "duration": 3, "description": "Formation avancée sur les Web Services en Python"},
    "java-avance-bases": {"code": "JAV100614-B", "titre": "Java Avancé : Bases", "level": "advanced", "duration": 5, "description": "Formation avancée sur les bases en Java"},
    "docker-initiation-conteneurs": {"code": "DOK100614-C", "titre": "Docker initiation : Conteneurs", "level": "beginner", "duration": 2, "description": "Formation d'initiation à Docker et aux conteneurs"},
}

# version uuid
FORMATIONS = {
    "e7b2af20-31ec-4d17-8b82-a0bf63b85084": {"code": "PYT100614-F", "titre": "Python Avancé : Web Services", "level": "advanced", "duration": 3, "description": "Formation avancée sur les Web Services en Python"},
    "e7b2af20-31ec-4d17-8b82-a0bf63b85085": {"code": "JAV100614-B", "titre": "Java Avancé : Bases", "level": "advanced", "duration": 5, "description": "Formation avancée sur les bases en Java"},
    "e7b2af20-31ec-4d17-8b82-a0bf63b85086": {"code": "DOK100614-C", "titre": "Docker initiation : Conteneurs", "level": "beginner", "duration": 2, "description": "Formation d'initiation à Docker et aux conteneurs"},
}

### REMARQUE: pour trouver la route correcte, FastAPI utilise l'ordre des décorateurs et la spécificité des chemins.
### règle générale: une route fixe doit être écrute AVANT une route dynamique
@router.get("/truc")
def lire_formation():
    return {"value": "truc"}



### possibilités pour un identifiant avec FastAPI

## 1/ int:
# @router.get("/{formation_id}")
# # ------------------------------------> version précédente: objet de contrainte sur un identifiant de chemin en tant que valeur par défaut !
# def lire_formation(formation_id: int = Path(gt=0)):
# --------------------------------> version récente avec annotation complexe
# def lire_formation(formation_id: Annotated[int, Path(gt=0)]):
#     return FORMATIONS_INT[formation_id - 1] or {}

# 2/ uuid: identifiant unique universel
@router.get("/{formation_id}")
# ------------------------------> ici les annotations peuvent être bloquantes
def lire_formation(formation_id: uuid.UUID):
    uid = str(formation_id)
    if uid not in FORMATIONS:
        raise HTTPException(status_code=404, detail=f"Formation {uid} introuvable.")
    return FORMATIONS.get(uid, {})

## 3/ slug: str unique avec lettre miniscules, chiffres et -
# @router.get("/{slug}")
# def lire_formation(slug: str = Path(min_length=3, max_length=100, regex="^[a-z0-9-]{3,}$")):
#     return FORMATIONS_SLUG.get(slug, {})


#### gestion des query params

# décorateur qui achemine le flux entrant sur cette fonctin
@router.get("")
def lister_formations(
    # --> annotation complexe
    # ------------------> contraintes de queryparams (?param=..&..)
    # ------------------------------------------------------------> véritable valeur par défaut
    size: Annotated[int, Query(alias="page[size]", ge=1, le=100)] = 25,
    after: Annotated[int, Query(alias="page[after]", ge=0)] = 0,
    level: Annotated[str, Query(alias="filter[level]")] = None,
    sort: Annotated[Literal["code", "-code", "titre", "-titre"], Query()] = "code"
):
    """
    handler = gestionnaire
    """
    results = FORMATIONS_INT[after:after + size]
    if level:
        results = list(filter(lambda f: f["level"] == level, results))
    
    return sorted(
        results, 
        key=lambda f: f.get(sort.lstrip("-")),
        reverse=sort.startswith("-")
    )
