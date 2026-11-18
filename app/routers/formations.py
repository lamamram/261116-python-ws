# app/routers/formations.py
from fastapi import APIRouter, Path, Query, HTTPException, Depends, Header
from typing import Annotated, Literal, List
import uuid
from datetime import datetime
from ..schemas.formations import FormationResponse, FormationCreate, FormationUpdate, Level
from ..auth import authenticate_basic

# objet router à connecter à l'app !
router = APIRouter(prefix="/formations", tags=["formations"])

# version entier
# FORMATIONS_INT = [
#     {"code": "PYT100614-F", "title": "Python Avancé : Web Services", "level": "advanced", "duration": 5, "description": "Formation avancée sur les Web Services en Python"},
#     {"code": "JAV100614-B", "title": "Java Avancé : Bases", "level": "advanced", "duration": 5, "description": "Formation avancée sur les bases en Java"},
#     {"code": "DOK100614-C", "title": "Docker initiation : Conteneurs", "level": "beginner", "duration": 3, "description": "Formation d'initiation à Docker et aux conteneurs"},
# ]

# # version slug
# FORMATIONS_SLUG = {
#     "python-avance-web-services": {"code": "PYT100614-F", "title": "Python Avancé : Web Services", "level": "advanced", "duration": 3, "description": "Formation avancée sur les Web Services en Python"},
#     "java-avance-bases": {"code": "JAV100614-B", "title": "Java Avancé : Bases", "level": "advanced", "duration": 5, "description": "Formation avancée sur les bases en Java"},
#     "docker-initiation-conteneurs": {"code": "DOK100614-C", "title": "Docker initiation : Conteneurs", "level": "beginner", "duration": 2, "description": "Formation d'initiation à Docker et aux conteneurs"},
# }

# version uuid
FORMATIONS = {
    "e7b2af20-31ec-4d17-8b82-a0bf63b85084": {
        "code": "PYT100614-F", 
        "title": "Python Avancé : Web Services",
        "level": "advanced", "duration": 3,
        "description": "Formation avancée sur les Web Services en Python",
        "created_at": "2024-06-26T12:00:00",
        "updated_at": "2024-06-26T12:00:00"
    },
    "e7b2af20-31ec-4d17-8b82-a0bf63b85085": {
        "code": "JAV100614-B", 
        "title": "Java Avancé : Bases", 
        "level": "advanced", 
        "duration": 5, 
        "description": "Formation avancée sur les bases en Java",
        "created_at": "2024-06-26T12:00:00",
        "updated_at": "2024-06-26T12:00:00"
    },
    "e7b2af20-31ec-4d17-8b82-a0bf63b85086": {
        "code": "DOK100614-C", 
        "title": "Docker initiation : Conteneurs", 
        "level": "beginner", 
        "duration": 2, 
        "description": "Formation d'initiation à Docker et aux conteneurs",
        "created_at": "2024-06-26T12:00:00",
        "updated_at": "2024-06-26T12:00:00"
    },
}


def _adapt_formation(obj: dict, uid: str) -> dict:
    obj["level"] = Level[obj["level"]].value
    obj["id"] = uid
    return obj


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
# -----------------------------------> avec çà la réponse est validée par le schéma !
@router.get("/{formation_id}", response_model=FormationResponse)
# ------------------------------> ici les annotations peuvent être bloquantes
def lire_formation(formation_id: uuid.UUID) -> FormationResponse:
    uid = str(formation_id)
    if uid not in FORMATIONS:
        raise HTTPException(status_code=404, detail=f"Formation {uid} introuvable.")
    obj = FORMATIONS.get(uid).copy()
    # remplacer la clé d'énum python par sa valeur !
    return _adapt_formation(obj, uid)

## 3/ slug: str unique avec lettre miniscules, chiffres et -
# @router.get("/{slug}")
# def lire_formation(slug: str = Path(min_length=3, max_length=100, regex="^[a-z0-9-]{3,}$")):
#     return FORMATIONS_SLUG.get(slug, {})


#### gestion des query params

# décorateur qui achemine le flux entrant sur cette fonction

# ---------------------------> liste de schémas
@router.get("", response_model=List[FormationResponse])
def lister_formations(
    # --> annotation complexe
    # ------------------> contraintes de queryparams (?param=..&..)
    # ------------------------------------------------------------> véritable valeur par défaut
    size: Annotated[int, Query(alias="page[size]", ge=1, le=100)] = 25,
    after: Annotated[int | None, Query(alias="page[after]")] = 0,
    level: Annotated[Level | None, Query(alias="filter[level]")] = None,
    sort: Annotated[Literal["code", "-code", "title", "-title"], Query()] = "code"
) -> List[FormationResponse]:
    """
    handler = gestionnaire => publiée dans /docs
    """
    # copie creuse profonde de FORMATIONS dict[str, dict]
    objs = [ (uid, f.copy()) for uid, f in FORMATIONS.copy().items() ]

    objs = list(map(
        lambda tup: _adapt_formation(tup[1], tup[0]),
        objs
    ))[after:after + size]

    if level:
        objs = list(filter(lambda f: Level[f["level"]].value == level, objs))

    return sorted(
        objs, 
        key=lambda f: f.get(sort.lstrip("-")),
        reverse=sort.startswith("-")
    )

@router.post("", status_code=201, response_model=FormationResponse)
def creer_formation(
    data: FormationCreate, 
    #  ------------------------------------>permet de récupérer la clé d'idempotence depuis l'en-tête HTTP "Idempotency-Key"
    idempotency_key: Annotated[str | None, Header()] = None
) -> FormationResponse:
    
    uid = uuid.uuid4()
    # ----------------------------------> data est une instance de FormationCreate, pas un dict
    if list(filter(lambda f: f["code"] == data.code, FORMATIONS.values())):
        raise HTTPException(status_code=409, detail=f"Formation {data.code} existe déjà.")
    data.level = Level(data.level).name
    FORMATIONS[uid] = data.model_dump()
    FORMATIONS[uid]["created_at"] = datetime.now()
    FORMATIONS[uid]["updated_at"] = datetime.now()

    return _adapt_formation(FORMATIONS[uid].copy(), uid)

# curl.exe -X POST http://127.0.0.1:8000/v1/formations -H "Content-Type: application/json" -d "{\"code\": \"RUS111111-R\", \"title\": \"Rust-initiation\", \"level\": \"beginner\", \"duration\": 3 "}"


@router.put("/{formation_id}", response_model=FormationResponse)
def mettre_a_jour_formation(formation_id: uuid.UUID, data: FormationUpdate) -> FormationResponse:
    uid = str(formation_id)
    if uid not in FORMATIONS:
        raise HTTPException(status_code=404, detail=f"Formation {uid} introuvable.")
    # ---------------> transformation en dict mais avec paramètrage
    # ---------------------------> ne modifie que les champs fournis dans la requête (en SQL SET param=value)
    update_data = data.model_dump(exclude_unset=True)
    FORMATIONS[uid].update(update_data)
    FORMATIONS[uid]["updated_at"] = datetime.now()

    return _adapt_formation(FORMATIONS[uid], uid)

@router.delete("/{formation_id}", status_code=204)
def supprimer_formation(formation_id: uuid.UUID, username: Annotated[str, Depends(authenticate_basic)]):
    uid = str(formation_id)
    if uid not in FORMATIONS:
        raise HTTPException(status_code=404, detail=f"Formation {uid} introuvable.")
    del FORMATIONS[uid]