import requests
from requests.auth import HTTPDigestAuth
from urllib.parse import urljoin

common_headers = {
    "Accept": "application/json"
}


class pyritrix():
    def __init__(self, hostname: str, username: str, password: str, port=8443, verify_certs=True):
        self.session = requests.Session()
        self.session.auth = HTTPDigestAuth(username, password)
        self.verify_certs = verify_certs
        self.base_url = f"https://{hostname}:{port}/"

    def get(self, path: str, **kwargs):
        return self.session.get(
            urljoin(self.base_url, path), headers=common_headers, verify=self.verify_certs, **kwargs)

    def status(self) -> dict:
        """
        Returns information about this instance of Heritrix such as version number, memory usage and the list of crawl jobs.
        """
        return self.get("/engine")
