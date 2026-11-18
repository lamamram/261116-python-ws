# app/routers/formations.py
from fastapi import APIRouter, Path
import uuid

# objet router à connecter à l'app !
router = APIRouter(prefix="/formations", tags=["formations"])

FORMATIONS = {
    "e7b2af20-31ec-4d17-8b82-a0bf63b85084": {"code": "PYT100614-F", "titre": "Python Avancé : Web Services"},
    "e7b2af20-31ec-4d17-8b82-a0bf63b85085": {"code": "JAV100614-B", "titre": "Java Avancé : Bases"},
    "e7b2af20-31ec-4d17-8b82-a0bf63b85086": {"code": "DOK100614-C", "titre": "Docker Avancé : Conteneurs"},
}


### autre possibilités
## 1/ slug: str unique avec lettre miniscules, chiffres et -
# @router.get("/{slug}")
# def lire_formation(slug: str = Path(max_length=100, pattern="[a-z0-9-]")):
## 2/ int:
# @router.get("/{formation_id}")
# def lire_formation(formation_id: int = Path(gt=0)):

@router.get("/{formation_id}")
# ------------------------------> ici les annotations peuvent être bloquantes
def lire_formation(formation_id: uuid.UUID):
    return FORMATIONS.get(str(formation_id), {})


# décorateur qui achemine le flux entrant sur cette fonctin
@router.get("")
def lister_formations():
    """
    handler = gestionnaire
    """
    ...
