# app/routers/formations.py
from fastapi import APIRouter, Path, Query, HTTPException, Depends
from typing import Annotated, Literal, List
import uuid
from ..schemas.formations import FormationSchema, FormationCreate, FormationUpdate, Level
from ..auth import authenticate

# objet router à connecter à l'app !
router = APIRouter(prefix="/formations", tags=["formations"])

# version entier
FORMATIONS_INT = [
    {"code": "PYT100614-F", "titre": "Python Avancé : Web Services", "level": "advanced", "duration": 5, "description": "Formation avancée sur les Web Services en Python"},
    {"code": "JAV100614-B", "titre": "Java Avancé : Bases", "level": "advanced", "duration": 5, "description": "Formation avancée sur les bases en Java"},
    {"code": "DOK100614-C", "titre": "Docker initiation : Conteneurs", "level": "beginner", "duration": 3, "description": "Formation d'initiation à Docker et aux conteneurs"},
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
# -----------------------------------> avec çà la réponse est validée par le schéma !
@router.get("/{formation_id}", response_model=FormationSchema)
# ------------------------------> ici les annotations peuvent être bloquantes
def lire_formation(formation_id: uuid.UUID):
    uid = str(formation_id)
    if uid not in FORMATIONS:
        raise HTTPException(status_code=404, detail=f"Formation {uid} introuvable.")
    result = FORMATIONS.get(uid)
    
    # remplacer la clé d'énum python par sa valeur !
    result["level"] = Level[result["level"]].value

    return result

## 3/ slug: str unique avec lettre miniscules, chiffres et -
# @router.get("/{slug}")
# def lire_formation(slug: str = Path(min_length=3, max_length=100, regex="^[a-z0-9-]{3,}$")):
#     return FORMATIONS_SLUG.get(slug, {})


#### gestion des query params

# décorateur qui achemine le flux entrant sur cette fonction

# ---------------------------> liste de schémas
@router.get("", response_model=List[FormationSchema])
def lister_formations(
    # --> annotation complexe
    # ------------------> contraintes de queryparams (?param=..&..)
    # ------------------------------------------------------------> véritable valeur par défaut
    size: Annotated[int, Query(alias="page[size]", ge=1, le=100)] = 25,
    after: Annotated[int, Query(alias="page[after]", ge=0)] = 0,
    level: Annotated[str, Query(alias="filter[level]")] = None,
    sort: Annotated[Literal["code", "-code", "titre", "-titre"], Query()] = "code"
) -> List[FormationSchema]:
    """
    handler = gestionnaire => publiée dans /docs
    """
    results = FORMATIONS_INT[after:after + size]
    if level:
        results = list(filter(lambda f: f["level"] == level, results))

    results = list(map(lambda f: {**f, "level": Level[f["level"]].value}, results))
    
    return sorted(
        results, 
        key=lambda f: f.get(sort.lstrip("-")),
        reverse=sort.startswith("-")
    )

@router.post("", status_code=201, response_model=FormationSchema)
def creer_formation(data: FormationCreate) -> FormationSchema:
    uid = uuid.uuid4()
    # ----------------------------------> data est une instance de FormationCreate, pas un dict
    if list(filter(lambda f: f["code"] == data.code, FORMATIONS.values())):
        raise HTTPException(status_code=409, detail=f"Formation {data.code} existe déjà.")
    FORMATIONS[uid] = dict(data)
    return FORMATIONS[uid]

# curl.exe -X POST http://127.0.0.1:8000/v1/formations -H "Content-Type: application/json" -d "{\"code\": \"CODE123\", \"titre\": \"Titre de la formation\", \"level\": \"beginner\"}"


@router.put("/{formation_id}", response_model=FormationSchema)
def mettre_a_jour_formation(formation_id: uuid.UUID, data: FormationUpdate) -> FormationSchema:
    uid = str(formation_id)
    if uid not in FORMATIONS:
        raise HTTPException(status_code=404, detail=f"Formation {uid} introuvable.")
    # ---------------> transformation en dict mais avec paramètrage
    # ---------------------------> ne modifie que les champs fournis dans la requête (en SQL SET param=value)
    update_data = data.model_dump(exclude_unset=True)
    FORMATIONS[uid]["level"] = Level[FORMATIONS[uid]["level"]].value
    FORMATIONS[uid].update(update_data)
    return FORMATIONS[uid]

@router.delete("/{formation_id}", status_code=204)
def supprimer_formation(formation_id: uuid.UUID, username: Annotated[str, Depends(authenticate)]):
    uid = str(formation_id)
    if uid not in FORMATIONS:
        raise HTTPException(status_code=404, detail=f"Formation {uid} introuvable.")
    del FORMATIONS[uid]