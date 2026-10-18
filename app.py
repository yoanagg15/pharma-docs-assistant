"""Bilingual Streamlit UI with per-session state and an explicit submission boundary."""

import hashlib
import json

import streamlit as st

from pharmaops.blob_storage import LocalProcedureStore, StorageError
from pharmaops.client import BusinessClient, BusinessError
from pharmaops.config import Settings
from pharmaops.i18n import translate
from pharmaops.knowledge import KnowledgeError, Retriever
from pharmaops.providers import ModelError, Provider
from pharmaops.schemas import fingerprint
from pharmaops.workflow import run_workflow

st.set_page_config(page_title="PharmaOps AI", page_icon="📦", layout="wide")
settings = Settings.load()
language_label = st.selectbox("Language / Език", ["English", "Български"], key="ui_language")
language = "bg" if language_label == "Български" else "en"


def t(text):
    return translate(text, language)


def localized_select(label, values, key):
    # Keep domain values stable while rebuilding translated display labels on language changes.
    previous_value = st.session_state.get("value_" + key, values[0])
    labels = [t(value) if value is not None else t("Choose country") for value in values]
    selected = st.selectbox(
        t(label), labels, index=values.index(previous_value), key=f"{key}_{language}"
    )
    value = values[labels.index(selected)]
    st.session_state["value_" + key] = value
    return value


st.title("PharmaOps AI")
st.markdown(
    f"**{t('Distribution Support Assistant')}** · "
    + t("Find procedure evidence and prepare delivery complaints.")
)
st.caption(
    t("LOCAL DEMO · FICTIONAL DATA · Independent portfolio project · Illustrative procedures only")
)
st.caption(t("Proof of Concept (PoC) · Synthetic pharmaceutical distribution data"))
st.caption(
    f"{t('Model mode')}: {settings.provider.upper()} · {settings.model} · "
    + t("Local semantic embeddings")
)
if settings.provider == "mock":
    st.warning(t("MOCK MODE — deterministic simulated responses. No real LLM is running."))
country = localized_select("Applicable country", [None, "BG", "DE", "RO"], "country")
with st.sidebar:
    st.subheader(t("Workspace"))
    st.info(f"{t('Provider')}: {settings.provider.upper()}\n\n{t('Model')}: {settings.model}")
    if settings.provider != "mock":
        st.caption(
            t("Model calls are sent to the configured provider. Use fictional information only.")
        )
    st.caption(
        t("Complaint country is checked against the delivery record. No production authentication.")
    )
    st.markdown(f"**{t('Demo delivery')}:** DEL-1002 ({t('Bulgaria')})")
    st.caption(
        t(
            "Services and the business API are local. "
            "The API represents a simulated external system."
        )
    )
    st.caption(t("Source procedures are fictional and written in English."))

context = [country, language]
if st.session_state.get("procedure_context") != context:
    st.session_state.pop("procedure_result", None)
st.session_state["procedure_context"] = context


def execute(**request):
    client = BusinessClient(settings.api_url)
    try:
        with st.spinner(t("Checking delivery procedures…")):
            return run_workflow(
                Provider(settings), Retriever(settings), client, language=language, **request
            )
    except (ModelError, KnowledgeError, BusinessError) as exc:
        st.error(t(str(exc)))
        return None
    except Exception:
        st.error(
            t(
                "The workflow could not complete. Check configuration and retry. "
                "No complaint was submitted by the workflow."
            )
        )
        return None
    finally:
        client.close()


def show_result(result):
    if result.get("country"):
        st.caption(f"{t('Applicable country')}: {result['country']}")
    st.write(t(result.get("message", "")))
    answer = result.get("answer")
    if answer and answer.supported:
        for claim in answer.claims:
            if language == "bg" and claim.translation_bg:
                st.write(claim.translation_bg)
                st.caption(t("Machine translation; verify against the original source."))
                with st.expander(t("Original English source excerpt")):
                    st.text(claim.quote)
            else:
                st.write(claim.quote)
            st.caption(f"{t('Source')}: {claim.citation_id}")
    with st.expander(t("Activity"), expanded=False):
        for item in result.get("trace", []):
            st.write("• " + t(item))
    for doc in result.get("evidence", []):
        m = doc.metadata
        with st.expander(f"{m['title']} · {m['section']}"):
            st.caption(
                f"{m['document_id']} · v{m['version']} · {m['country']} · "
                f"{t('Effective')} {m['effective_date']} · {m['chunk_id']}"
            )
            st.text(doc.page_content)


procedures, complaints, documents = st.tabs(
    [t("Procedure questions"), t("Delivery complaints"), t("Document storage")]
)
with procedures:
    st.subheader(t("Find the next operational step"))
    question = st.text_input(
        t("Your procedure question"),
        max_chars=1500,
        value=t("What should I do if a delivery arrives with damaged outer packaging?"),
    )
    if st.button(t("Find procedure"), type="primary"):
        result = execute(question=question, mode="procedure", country=country)
        if result:
            st.session_state["procedure_result"] = result
    if "procedure_result" in st.session_state:
        show_result(st.session_state["procedure_result"])

with complaints:
    st.subheader(t("Prepare → review → confirm"))
    st.caption(
        t(
            "The assistant can save a draft. "
            "Only your confirmation button submits it to the simulated API."
        )
    )
    left, right = st.columns(2)
    with left:
        delivery_id = st.text_input(
            t("Delivery identifier"), value="DEL-1002", max_chars=20, key="delivery_id"
        )
        category = localized_select(
            "Complaint category",
            ["damaged_packaging", "missing_items", "discrepancy", "return_request"],
            "category",
        )
        description = st.text_area(
            t("Factual description (required, 10–1,500 characters)"),
            max_chars=1500,
            key="description",
            placeholder=t("Describe the visible issue and any relevant counts."),
        )
    with right:
        affected = st.number_input(
            t("Affected packages"), min_value=1, max_value=1000, value=1, key="affected_packages"
        )
        resolution = localized_select(
            "Requested resolution",
            ["investigation", "replacement_review", "return_review"],
            "requested_resolution",
        )
        st.caption(
            t(
                "No emails are sent. "
                "Recording a complaint does not authorize returns or replacement stock."
            )
        )
    fields = {
        "delivery_id": delivery_id.strip().upper(),
        "category": category,
        "description": description.strip(),
        "affected_packages": affected,
        "requested_resolution": resolution,
    }
    snapshot = hashlib.sha256(json.dumps([fields, country], sort_keys=True).encode()).hexdigest()
    previous = st.session_state.get("draft")
    if st.button(t("Prepare / update draft"), type="primary"):
        result = execute(
            question=f"Report {category.replace('_', ' ')} for {fields['delivery_id']}.",
            mode="complaint",
            country=country,
            fields=fields,
            previous_draft=previous,
        )
        st.session_state["complaint_result"] = result
        if result and result.get("draft"):
            st.session_state["draft"] = result["draft"]
            st.session_state["draft_snapshot"] = snapshot
            st.session_state.pop("receipt", None)
    if st.session_state.get("complaint_result"):
        show_result(st.session_state["complaint_result"])
    draft = st.session_state.get("draft")
    if draft:
        st.markdown(f"**{t('Draft preview')}**")
        # Display translated labels without changing the canonical API payload or fingerprint.
        preview = {t(k): t(v) if isinstance(v, str) else v for k, v in draft.model_dump().items()}
        st.json(preview, expanded=True)
        current = snapshot == st.session_state.get("draft_snapshot")
        key = "confirmation_" + fingerprint(draft)
        if not current:
            st.session_state[key] = False
            st.warning(t("Fields changed. Update the draft and review it again before confirming."))
        reviewed = st.checkbox(
            t("I reviewed this exact draft and confirm submission to the simulated API."),
            key=key,
            disabled=not current,
        )
        if st.button(t("Confirm and submit complaint"), disabled=not (reviewed and current)):
            client = BusinessClient(settings.api_url)
            try:
                st.session_state["receipt"] = client.submit(draft)
            except BusinessError as exc:
                st.error(t(str(exc)))
            finally:
                client.close()
        if "receipt" in st.session_state:
            receipt = st.session_state["receipt"]
            st.success(f"{t('Complaint recorded')}: {receipt.reference}")
            if receipt.duplicate:
                st.caption(t("This draft was already submitted. The same reference was returned."))
        if st.button(t("Start a new complaint")):
            for name in ("draft", "draft_snapshot", "receipt", "complaint_result"):
                st.session_state.pop(name, None)
            st.rerun()

with documents:
    st.subheader(t("Fictional procedure library"))
    st.caption(t("LOCAL AZURITE EMULATOR · Azure Blob SDK · No Azure account or subscription"))
    st.write(
        t("Publish the seven seeded procedures, inspect metadata, and download verified originals.")
    )
    st.caption(
        t(
            "This library is a storage exercise. "
            "Procedure answers still use the local indexed corpus."
        )
    )

    def storage_action(action):
        storage = LocalProcedureStore()
        try:
            with st.spinner(t("Contacting local procedure storage…")):
                return action(storage)
        except StorageError as exc:
            st.error(t(str(exc)))
            return None
        finally:
            storage.close()

    if st.button(t("Publish demo procedures")):

        def publish_and_list(storage):
            storage.publish()
            return storage.list_procedures()

        records = storage_action(publish_and_list)
        if records is not None:
            st.session_state["stored_procedures"] = records
            st.session_state.pop("blob_download", None)
            st.success(t("Demo procedures published to local storage."))
    if st.button(t("Refresh stored procedures")):
        records = storage_action(lambda storage: storage.list_procedures())
        if records is not None:
            st.session_state["stored_procedures"] = records
            st.session_state.pop("blob_download", None)
    records = st.session_state.get("stored_procedures", [])
    if not records:
        st.info(t("No procedures loaded. Start Azurite, then publish or refresh."))
    else:
        name = st.selectbox(t("Stored procedure"), [record.name for record in records])
        record = next(record for record in records if record.name == name)
        st.json(
            {
                "name": record.name,
                "bytes": record.size,
                "etag": record.etag,
                **record.metadata.model_dump(),
            }
        )
        if st.button(t("Prepare verified download")):
            data = storage_action(lambda storage: storage.download(name))
            if data is not None:
                st.session_state["blob_download"] = (name, data)
        prepared = st.session_state.get("blob_download")
        if prepared and prepared[0] == name:
            st.download_button(
                t("Download original procedure"),
                data=prepared[1],
                file_name=name,
                mime="text/markdown",
            )
            st.caption(t("SHA-256 and document metadata checked. Original English source."))
