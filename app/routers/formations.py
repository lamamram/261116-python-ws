# app/routers/formations.py
from fastapi import APIRouter, Path
import uuid

# objet router à connecter à l'app !
router = APIRouter(prefix="/formations", tags=["formations"])

# version entier
FORMTIONS_INT = [
    {"code": "PYT100614-F", "titre": "Python Avancé : Web Services"},
    {"code": "JAV100614-B", "titre": "Java Avancé : Bases"},
    {"code": "DOK100614-C", "titre": "Docker Avancé : Conteneurs"},
]

FORMATIONS_SLUG = {
    "python-avance-web-services": {"code": "PYT100614-F", "titre": "Python Avancé : Web Services"},
    "java-avance-bases": {"code": "JAV100614-B", "titre": "Java Avancé : Bases"},
    "docker-avance-conteneurs": {"code": "DOK100614-C", "titre": "Docker Avancé : Conteneurs"},
}

# version uuid
FORMATIONS = {
    "e7b2af20-31ec-4d17-8b82-a0bf63b85084": {"code": "PYT100614-F", "titre": "Python Avancé : Web Services"},
    "e7b2af20-31ec-4d17-8b82-a0bf63b85085": {"code": "JAV100614-B", "titre": "Java Avancé : Bases"},
    "e7b2af20-31ec-4d17-8b82-a0bf63b85086": {"code": "DOK100614-C", "titre": "Docker Avancé : Conteneurs"},
}

### REMARQUE: pour trouver la route correcte, FastAPI utilise l'ordre des décorateurs et la spécificité des chemins.
### règle générale: une route fixe doit être écrute AVANT une route dynamique
@router.get("/truc")
def lire_formation():
    return {"value": "truc"}



### possibilités pour un identifiant avec FastAPI

## 1/ int:
# @router.get("/{formation_id}")
# # ------------------------------------> objet de contrainte sur un identifiant de chemin
# def lire_formation(formation_id: int = Path(gt=0)):
#     return FORMTIONS_INT[formation_id - 1] or {}

# 2/ uuid: identifiant unique universel
@router.get("/{formation_id}")
# ------------------------------> ici les annotations peuvent être bloquantes
def lire_formation(formation_id: uuid.UUID):
    return FORMATIONS.get(str(formation_id), {})

## 3/ slug: str unique avec lettre miniscules, chiffres et -
# @router.get("/{slug}")
# def lire_formation(slug: str = Path(min_length=3, max_length=100, regex="^[a-z0-9-]{3,}$")):
#     return FORMATIONS_SLUG.get(slug, {})

# décorateur qui achemine le flux entrant sur cette fonctin
@router.get("")
def lister_formations():
    """
    handler = gestionnaire
    """
    ...
