from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing import Annotated
from fastapi import Depends, HTTPException
import secrets

schema_basic = HTTPBasic(auto_error=False)


def authenticate_basic(
        # --------------> schéma pydantic pour certifier que on a username et passowrd dedans
        # ---------------------------------------------------> classe fastapi qui gère (décodage..) la str base64 encodée du entête Authorization: Basic erjfekrfbre==
        # -------------------------------------------> injection dépendance contrôlée par FASTAPI (
        #                                                             place la gestion de dépendance dans le cycle de vie d'une requête
        #                                                             exécute et valide la dépendance
        #                                                             fonctionne en synchrone et en asychrone
        creds: Annotated[HTTPBasicCredentials | None, Depends(schema_basic)]
):
    if creds is None or not (
        secrets.compare_digest(creds.username.encode("utf-8"), b"bob") and 
        secrets.compare_digest(creds.password.encode("utf-8"), b"roottoor")
    ):
        raise HTTPException(
            status_code=401, 
            detail="invalid_credentials: Identifiant ou mot de passe incorrect.",
            headers={"WWW-Authenticate": 'Basic realm="generic"'}
        )
    return creds.username