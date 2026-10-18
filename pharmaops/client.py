"""Actual HTTP client; the UI and agents never open the business database."""

import httpx
from pydantic import ValidationError

from pharmaops.schemas import Confirmation, Delivery, Draft, Receipt, fingerprint


class BusinessError(Exception):
    pass


class BusinessClient:
    def __init__(self, base_url, transport=None):
        self.http = httpx.Client(base_url=base_url, timeout=5, transport=transport, trust_env=False)

    def close(self):
        self.http.close()

    def _request(self, method, path, schema, **kwargs):
        try:
            response = self.http.request(method, path, **kwargs)
            if response.status_code == 404:
                raise BusinessError("Delivery or draft not found. Check the identifier.")
            if response.status_code == 409:
                raise BusinessError("Draft changed or was already submitted. Review it again.")
            if response.status_code == 422:
                raise BusinessError("Required fields do not match the delivery. Review your draft.")
            response.raise_for_status()
            return schema.model_validate(response.json())
        except (httpx.HTTPError, ValueError, ValidationError) as exc:
            raise BusinessError(
                "Simulated business API unavailable or invalid. Start the API "
                "and retry; an interrupted submission can safely be retried."
            ) from exc

    def delivery(self, delivery_id):
        return self._request("GET", f"/deliveries/{delivery_id}", Delivery)

    def save(self, draft):
        return self._request("PUT", f"/drafts/{draft.draft_id}", Draft, json=draft.model_dump())

    def submit(self, draft):
        # Called exclusively by the explicit UI action, never exposed as an agent tool.
        digest = fingerprint(draft)
        confirmation = Confirmation(
            draft_id=draft.draft_id, revision=draft.revision, fingerprint=digest, confirmed=True
        )
        return self._request(
            "POST",
            "/complaints",
            Receipt,
            json=confirmation.model_dump(),
            headers={"Idempotency-Key": digest},
        )
