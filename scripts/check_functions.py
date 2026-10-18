"""Exercise real localhost Azure Functions HTTP transport; no cloud or model requests.

Creates one clearly fictional draft/complaint to verify the adapter's existing API contract.
"""

import json
from uuid import uuid4

import httpx

from pharmaops.client import BusinessClient
from pharmaops.schemas import Confirmation, Draft, fingerprint


def main():
    base_url = "http://127.0.0.1:7071"
    client = BusinessClient(base_url)
    with httpx.Client(base_url=base_url, timeout=10, trust_env=False) as http:
        try:
            health = http.get("/health")
            health.raise_for_status()
            assert health.json() == {"status": "ok", "simulation": True}
            delivery = client.delivery("DEL-1002")
            assert delivery.country == "BG"
            assert http.get("/deliveries/DEL-9999").status_code == 404
            draft = Draft(
                delivery_id=delivery.delivery_id,
                category="damaged_packaging",
                description="Fictional Azure Functions adapter check: outer carton corner torn.",
                affected_packages=1,
                requested_resolution="investigation",
                draft_id="functions-check-" + uuid4().hex,
                revision=1,
                country=delivery.country,
                source_ids=["SOP-DAMAGE-v2.0-ea286b1ecb27"],
            )
            assert client.save(draft) == draft
            stale = Confirmation(
                draft_id=draft.draft_id, revision=1, fingerprint=fingerprint(draft), confirmed=True
            )
            updated = draft.model_copy(
                update={"revision": 2, "description": draft.description + " Updated check."}
            )
            client.save(updated)
            assert (
                http.post(
                    "/complaints",
                    json=stale.model_dump(),
                    headers={"Idempotency-Key": stale.fingerprint},
                ).status_code
                == 409
            )
            first = client.submit(updated)
            again = client.submit(updated)
            assert first.reference == again.reference and again.duplicate
            print(
                json.dumps(
                    {
                        "runtime": "Azure Functions Core Tools, localhost",
                        "health": "passed",
                        "delivery_lookup": "passed",
                        "unknown_delivery": "passed",
                        "stale_confirmation": "rejected",
                        "duplicate_submission": "same reference",
                        "fictional_complaint_reference": first.reference,
                    },
                    indent=2,
                )
            )
        finally:
            client.close()


if __name__ == "__main__":
    main()
