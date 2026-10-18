from concurrent.futures import ThreadPoolExecutor

import httpx
import pytest

from pharmaops.client import BusinessClient, BusinessError
from pharmaops.schemas import fingerprint


def submit(api, draft, **updates):
    body = {
        "draft_id": draft.draft_id,
        "revision": draft.revision,
        "fingerprint": fingerprint(draft),
        "confirmed": True,
        **updates,
    }
    return api.post("/complaints", json=body, headers={"Idempotency-Key": fingerprint(draft)})


def test_health_and_unknown_delivery(api):
    assert api.get("/health").json()["simulation"]
    assert api.get("/deliveries/DEL-9999").status_code == 404
    assert api.get("/deliveries/DEL-1002").json()["country"] == "BG"


def test_missing_fields_and_confirmation_blocked(api, draft):
    invalid = draft.model_dump(exclude={"description"})
    assert api.put("/drafts/test-draft", json=invalid).status_code == 422
    assert api.put("/drafts/test-draft", json=draft.model_dump()).status_code == 200
    assert submit(api, draft, confirmed=False).status_code == 422
    assert submit(api, draft, confirmed=None).status_code == 422


def test_changed_draft_invalidates_confirmation(api, draft):
    api.put("/drafts/test-draft", json=draft.model_dump())
    changed = draft.model_copy(update={"description": "Two outer cartons are torn.", "revision": 2})
    assert api.put("/drafts/test-draft", json=changed.model_dump()).status_code == 200
    assert submit(api, draft).status_code == 409
    assert submit(api, changed).status_code == 200


def test_repeated_and_concurrent_submission_is_idempotent(api, draft):
    api.put("/drafts/test-draft", json=draft.model_dump())
    with ThreadPoolExecutor(max_workers=4) as pool:
        responses = list(pool.map(lambda _: submit(api, draft), range(4)))
    assert all(r.status_code == 200 for r in responses)
    assert len({r.json()["reference"] for r in responses}) == 1
    assert sum(not r.json()["duplicate"] for r in responses) == 1
    assert api.put("/drafts/test-draft", json=draft.model_dump()).status_code == 409


def test_delivery_validation_and_key_binding(api, draft):
    for update in ({"delivery_id": "DEL-9999"}, {"affected_packages": 500}, {"country": "DE"}):
        invalid = draft.model_copy(update=update)
        assert api.put("/drafts/test-draft", json=invalid.model_dump()).status_code in {404, 422}
    api.put("/drafts/test-draft", json=draft.model_dump())
    body = {
        "draft_id": draft.draft_id,
        "revision": 1,
        "fingerprint": fingerprint(draft),
        "confirmed": True,
    }
    assert (
        api.post("/complaints", json=body, headers={"Idempotency-Key": "wrong"}).status_code == 409
    )


def test_api_failure_is_useful():
    def unavailable(_request):
        raise httpx.ConnectError("do not expose raw network details")

    client = BusinessClient("http://localhost", httpx.MockTransport(unavailable))
    with pytest.raises(BusinessError, match="Start the API"):
        client.delivery("DEL-1002")
    client.close()


def test_http_client_uses_api_contract(api, draft):
    def route(request):
        response = api.request(
            request.method,
            request.url.raw_path.decode(),
            content=request.content,
            headers=dict(request.headers),
        )
        return httpx.Response(response.status_code, json=response.json())

    client = BusinessClient("http://localhost", httpx.MockTransport(route))
    assert client.delivery("DEL-1002").country == "BG"
    assert client.save(draft) == draft
    assert not client.submit(draft).duplicate
    assert client.submit(draft).duplicate
    with pytest.raises(BusinessError, match="not found"):
        client.delivery("DEL-9999")
    client.close()
