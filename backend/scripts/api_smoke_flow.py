from __future__ import annotations

import json
import os
import time
import uuid
from http.cookiejar import CookieJar
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import HTTPCookieProcessor, Request, build_opener


BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:9000")


class ApiClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/") + "/"
        self.opener = build_opener(HTTPCookieProcessor(CookieJar()))

    def json(self, method: str, path: str, payload: dict | None = None) -> dict:
        data = None
        headers = {"Accept": "application/json"}
        if payload is not None:
            data = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"
        return self._request(method, path, data=data, headers=headers)

    def multipart(self, path: str, fields: dict[str, str], files: dict[str, tuple[str, bytes, str]]) -> dict:
        boundary = f"----ibs-smoke-{uuid.uuid4().hex}"
        body = bytearray()
        for name, value in fields.items():
            body.extend(f"--{boundary}\r\n".encode())
            body.extend(f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode())
            body.extend(str(value).encode("utf-8"))
            body.extend(b"\r\n")
        for name, (filename, content, content_type) in files.items():
            body.extend(f"--{boundary}\r\n".encode())
            body.extend(
                (
                    f'Content-Disposition: form-data; name="{name}"; filename="{filename}"\r\n'
                    f"Content-Type: {content_type}\r\n\r\n"
                ).encode()
            )
            body.extend(content)
            body.extend(b"\r\n")
        body.extend(f"--{boundary}--\r\n".encode())
        return self._request(
            "POST",
            path,
            data=bytes(body),
            headers={
                "Accept": "application/json",
                "Content-Type": f"multipart/form-data; boundary={boundary}",
            },
        )

    def _request(self, method: str, path: str, data: bytes | None, headers: dict[str, str]) -> dict:
        request = Request(urljoin(self.base_url, path.lstrip("/")), data=data, headers=headers, method=method)
        try:
            with self.opener.open(request, timeout=20) as response:
                payload = response.read().decode("utf-8")
        except HTTPError as exc:
            detail = exc.read().decode("utf-8")
            raise RuntimeError(f"{method} {path} failed with {exc.code}: {detail}") from exc
        except URLError as exc:
            raise RuntimeError(
                f"{method} {path} failed: API is not available at {self.base_url}. "
                "Start MongoDB and backend first."
            ) from exc
        return json.loads(payload) if payload else {}


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def upload_indicator(client: ApiClient, name: str, values: list[tuple[str, int, int]]) -> dict:
    csv_rows = ["region,2023,2024"]
    csv_rows.extend(f"{region},{value_2023},{value_2024}" for region, value_2023, value_2024 in values)
    csv_bytes = ("\n".join(csv_rows) + "\n").encode("utf-8")
    return client.multipart(
        "/indicator/upload",
        fields={"name": name, "description": "smoke indicator"},
        files={"file": (f"{name}.csv", csv_bytes, "text/csv")},
    )


def main() -> None:
    suffix = f"{int(time.time())}-{uuid.uuid4().hex[:8]}"
    client = ApiClient(BASE_URL)

    user = client.json(
        "POST",
        "/user/register/",
        {
            "email": f"smoke-{suffix}@example.com",
            "username": f"smoke-{suffix}",
            "password": "secret123",
        },
    )
    assert_true(bool(user.get("id")), "register must return user id")

    login = client.json(
        "POST",
        "/user/login/",
        {"email": f"smoke-{suffix}@example.com", "password": "secret123"},
    )
    assert_true(login.get("ok") is True, "login must return ok=true")

    check = client.json("GET", "/user/check/")
    assert_true(check.get("ok") is True, "check must confirm authenticated user")

    first = upload_indicator(
        client,
        f"birth-{suffix}",
        [("Tomsk", 10, 12), ("Omsk", 8, 9), ("Novosibirsk", 15, 16)],
    )
    second = upload_indicator(
        client,
        f"income-{suffix}",
        [("Tomsk", 100, 130), ("Omsk", 90, 110), ("Novosibirsk", 140, 150)],
    )
    assert_true(first["preview_region_count"] == 3, "first upload must parse 3 regions")
    assert_true(second["preview_year_count"] == 2, "second upload must parse 2 years")

    project = client.json(
        "POST",
        "/project/",
        {"name": f"project-{suffix}", "description": ""},
    )
    assert_true(project["indicators"] == [], "new project must be empty")

    project_id = project["id"]
    project = client.json("POST", f"/project/{project_id}/indicators", {"indicator_id": first["id"]})
    project = client.json("POST", f"/project/{project_id}/indicators", {"indicator_id": second["id"]})
    assert_true(len(project["indicators"]) == 2, "project must contain two base indicators")

    for method in ["equal", "std", "pca", "modified_pca", "entropy"]:
        calculated = client.json(
            "POST",
            f"/project/{project_id}/calculate",
            {"year": "2024", "weight_method": method},
        )
        result = calculated["last_result"]
        weights = result["weights"]
        assert_true(result["weight_method"] == method, f"{method}: result must report selected method")
        assert_true(len(result["normalized_indicators"]) == 2, f"{method}: must normalize two indicators")
        assert_true(len(weights) == 2, f"{method}: must produce two weights")
        assert_true(abs(sum(item["weight"] for item in weights) - 1) < 1e-9, f"{method}: weights sum must be 1")
        assert_true(len(result["integral_values"]) == 3, f"{method}: must produce values for 3 regions")
        assert_true(len(result["ranking"]) == 3, f"{method}: must produce ranking for 3 regions")

    print("OK: register -> login -> upload -> empty project -> attach indicators -> normalize -> weights -> aggregate")


if __name__ == "__main__":
    main()
