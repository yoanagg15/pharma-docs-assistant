"""Simulated business API. SQLite is owned exclusively by this service."""

import json
import sqlite3
from contextlib import asynccontextmanager, contextmanager
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, Header, HTTPException

from pharmaops.config import Settings
from pharmaops.schemas import Confirmation, Delivery, Draft, Receipt, fingerprint


@contextmanager
def connect(path):
    with sqlite3.connect(path, timeout=10) as db:
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys=ON")
        yield db


def initialize(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with connect(path) as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS deliveries(id TEXT PRIMARY KEY, payload TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS drafts(
          id TEXT PRIMARY KEY, revision INTEGER NOT NULL, fingerprint TEXT NOT NULL,
          payload TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS complaints(
          reference TEXT PRIMARY KEY, draft_id TEXT NOT NULL UNIQUE REFERENCES drafts(id),
          idempotency_key TEXT NOT NULL UNIQUE, fingerprint TEXT NOT NULL, payload TEXT NOT NULL);
        """)
        countries = ["BG", "DE", "RO"]
        centers = {"BG": "Aster Sofia", "DE": "Aster Leipzig", "RO": "Aster Brasov"}
        for i in range(10):
            country = countries[(i + 2) % 3]  # DEL-1002 is BG for the demo.
            delivery = Delivery(
                delivery_id=f"DEL-{1001 + i}",
                country=country,
                distribution_center=centers[country],
                recipient=f"Fictional Pharmacy {i + 1}",
                packages=12 + i,
                status="delivered",
            )
            db.execute(
                "INSERT OR IGNORE INTO deliveries VALUES (?, ?)",
                (delivery.delivery_id, delivery.model_dump_json()),
            )


def create_app(db_path: Path | None = None):
    path = db_path or Settings.load().runtime / "business.sqlite3"

    @asynccontextmanager
    async def lifespan(_app):
        initialize(path)
        yield

    api = FastAPI(
        title="PharmaOps simulated business API",
        lifespan=lifespan,
        description="Local demo with fictional data. No production authentication.",
    )

    def get_delivery(db, delivery_id):
        row = db.execute("SELECT payload FROM deliveries WHERE id=?", (delivery_id,)).fetchone()
        if not row:
            raise HTTPException(404, "Unknown fictional delivery. Check the identifier.")
        return Delivery.model_validate_json(row["payload"])

    @api.get("/health")
    def health():
        return {"status": "ok", "simulation": True}

    @api.get("/deliveries/{delivery_id}", response_model=Delivery)
    def delivery(delivery_id: str):
        with connect(path) as db:
            return get_delivery(db, delivery_id)

    @api.put("/drafts/{draft_id}", response_model=Draft)
    def save_draft(draft_id: str, draft: Draft):
        if draft_id != draft.draft_id:
            raise HTTPException(422, "Draft identifier mismatch.")
        with connect(path) as db:
            db.execute("BEGIN IMMEDIATE")
            delivery = get_delivery(db, draft.delivery_id)
            if delivery.country != draft.country or draft.affected_packages > delivery.packages:
                raise HTTPException(422, "Country or package count does not match the delivery.")
            if db.execute("SELECT 1 FROM complaints WHERE draft_id=?", (draft_id,)).fetchone():
                raise HTTPException(409, "Submitted drafts cannot be changed. Create a new draft.")
            old = db.execute("SELECT * FROM drafts WHERE id=?", (draft_id,)).fetchone()
            digest = fingerprint(draft)
            if old:
                if old["fingerprint"] == digest:
                    return draft
                if draft.revision != old["revision"] + 1:
                    raise HTTPException(409, "Stale draft revision. Review the latest draft.")
            elif draft.revision != 1:
                raise HTTPException(409, "New drafts must start at revision 1.")
            db.execute(
                """INSERT INTO drafts VALUES (?, ?, ?, ?)
                       ON CONFLICT(id) DO UPDATE SET revision=excluded.revision,
                       fingerprint=excluded.fingerprint, payload=excluded.payload""",
                (draft_id, draft.revision, digest, draft.model_dump_json()),
            )
            return draft

    @api.post("/complaints", response_model=Receipt)
    def submit(confirmation: Confirmation, idempotency_key: str = Header(max_length=100)):
        with connect(path) as db:
            db.execute("BEGIN IMMEDIATE")  # Serialize check + insert, including concurrent retries.
            row = db.execute("SELECT * FROM drafts WHERE id=?", (confirmation.draft_id,)).fetchone()
            if not row:
                raise HTTPException(404, "Draft not found. Prepare a draft first.")
            if (
                row["revision"] != confirmation.revision
                or row["fingerprint"] != confirmation.fingerprint
            ):
                raise HTTPException(409, "Draft changed. Review and confirm the current revision.")
            if idempotency_key != confirmation.fingerprint:
                raise HTTPException(409, "Idempotency key must match the confirmed draft.")
            draft = Draft.model_validate_json(row["payload"])
            get_delivery(db, draft.delivery_id)
            previous = db.execute(
                "SELECT * FROM complaints WHERE draft_id=?", (draft.draft_id,)
            ).fetchone()
            if previous:
                return Receipt(
                    reference=previous["reference"], draft_id=draft.draft_id, duplicate=True
                )
            reference = "CMP-" + uuid4().hex[:12].upper()
            db.execute(
                "INSERT INTO complaints VALUES (?, ?, ?, ?, ?)",
                (
                    reference,
                    draft.draft_id,
                    idempotency_key,
                    confirmation.fingerprint,
                    json.dumps(draft.model_dump()),
                ),
            )
            return Receipt(reference=reference, draft_id=draft.draft_id)

    return api


app = create_app()
