from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .pyritrix import pyritrix


class JobsEndpoint:
    def __init__(self, client: pyritrix):
        self._client = client

    def create(self, createpath: str, profile=None) -> dict:
        """
        Creates a new crawl job from the selected profile. 
        If no profile is supplied, Defaults (XML) is used.
        Built-in profiles include Defaults (XML) and Defaults (Groovy).
        Existing job profiles may also be selected by passing the profile job’s short name.
        Arguments:
            createpath: the name of the new job
            profile: optional profile name. Existing profiles use their job short names.
        """
        data = {
            "action": "create",
            "createpath": createpath,
            "profile": profile  # It's fine, requests will omit this if profile=None
        }
        response = self._client.post("/engine", data=data)
        assert response.status_code == 200
        return response.json()
