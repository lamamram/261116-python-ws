from .config import Settings
from typing import Any
from urllib.parse import quote
from collections.abc import Iterator
import requests

class GoRestClient:
    """
    classe qui rélise une couche d'indirection pour masquer l'utilisation de requests/urllib3 ... et HTTP
    c'est un gestionnaire de contexte qui ouvre et ferme des sessions requests
    """
    def __init__(
            self, 
            settings: Settings | None = None, 
            headers: dict[str, Any]={}
        ):
        self.settings = settings or Settings.form_env()
        # ------------------------------------> gérer le / final s'il existe !
        self.base_url = self.settings.base_url.rstrip("/")

        # entêtes par défauts
        self.headers = { 
            **headers, 
            "Accept": "application/json",
            "User-Agent": "gorest-client/1.0"
        }

    ### trnasforme une classe custom en gestionnaire de contexte

    def __enter__(self):
        """
        cette méthode doit retourner un objet qui contient la session à droite du "as"
        """
        self.session = requests.Session()
        self.session.headers = self.headers
        return self

    def __exit__(self, exc_type, exc, tb):
        self.session.close()

    ### socle ##################################

    def __call(self, method: str, path: str, **options: Any):
        """
        **options couvre: params, data, cookies, files
        """
        options.setdefault("timeout", self.settings.timeout)
        print(options)
        options.setdefault("allow_redirects", self.settings.allow_redirects)
        url = f"{self.base_url}/{path.lstrip('/')}"

        # crée une request.Request + prepare + send
        r = self.session.request(method=method, url=url, **options)

        if r.ok and "application/json" in r.headers["content-type"]:
            return r.json()
        if "application/json" not in r.headers["content-type"]:
            raise "???"
        raise "???"

    ### helper #############################
    @staticmethod
    def _path(resource: str, _id: str) -> str:
        return f"{resource}/{quote(_id, safe='')}"

    ### interface publique ###################################

    def list(
            self, resource: str, 
            params: dict[str, Any] = {},
            taille: int = 5
        ) -> Iterator[dict[str, Any]]:
            params = {**params, "page[size]": taille}
            while True:
                # -------------------------------> appel nommé k=v => mis auto. dans **options
                obj = self.__call("GET", resource, params=params)
                yield from obj["data"]
                if not obj["meta"]["has_more"]:
                    return
                params["page[after]"] = obj["meta"]["next_cursor"]

    def get(self, resource: str, _id: str) -> dict[str, Any]:
        return self.__call("GET", self._path(resource, _id))





    