import requests


class ApiClient:
    """Thin wrapper around requests that handles base URL and the auth token."""

    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.token = None

    def request(self, method: str, path: str, headers: dict | None = None, **kwargs):
        all_headers = {}
        if self.token:
            all_headers["Authorization"] = f"Bearer {self.token}"
        if headers:
            all_headers.update(headers)  # lets a test override or break the header
        return self.session.request(
            method, f"{self.base_url}{path}", headers=all_headers, timeout=10, **kwargs
        )

    def login(self, email: str, password: str):
        return self.request("POST", "/api/login", json={"email": email, "password": password})

    def authenticate(self, email="test@example.com", password="Password123"):
        response = self.login(email, password)
        response.raise_for_status()
        self.token = response.json()["token"]
        return self

    def get(self, path, **kwargs):
        return self.request("GET", path, **kwargs)

    def post(self, path, **kwargs):
        return self.request("POST", path, **kwargs)

    def put(self, path, **kwargs):
        return self.request("PUT", path, **kwargs)

    def delete(self, path, **kwargs):
        return self.request("DELETE", path, **kwargs)