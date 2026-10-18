"""Streamlit session checks exercise the visible confirmation gate without a real model."""

from unittest.mock import patch

from streamlit.testing.v1 import AppTest

from pharmaops.config import ROOT, Settings


def test_mock_label_and_initial_empty_state():
    with patch("pharmaops.config.Settings.load", return_value=Settings()):
        app = AppTest.from_file(ROOT / "app.py").run()
    assert not app.exception
    assert any("MOCK MODE" in w.value for w in app.warning)
    assert not any(b.label == "Confirm and submit complaint" for b in app.button)


def test_editing_draft_invalidates_ui_confirmation(draft):
    result = {"draft": draft, "message": "Draft ready for review.", "trace": [], "evidence": []}
    with (
        patch("pharmaops.config.Settings.load", return_value=Settings()),
        patch("pharmaops.workflow.run_workflow", return_value=result),
        patch("pharmaops.knowledge.Retriever"),
        patch("pharmaops.client.BusinessClient"),
    ):
        app = AppTest.from_file(ROOT / "app.py").run()
        app.text_area[0].set_value("Outer carton torn at the corner.").run()
        next(b for b in app.button if b.label == "Prepare / update draft").click().run()
        assert not app.exception
        app.checkbox[0].check().run()
        confirm = next(b for b in app.button if b.label == "Confirm and submit complaint")
        assert not confirm.disabled
        app.text_area[0].set_value("Description changed after draft review.").run()
        confirm = next(b for b in app.button if b.label == "Confirm and submit complaint")
        assert confirm.disabled
        assert not app.checkbox[0].value


def test_country_change_clears_previous_procedure_result():
    with patch("pharmaops.config.Settings.load", return_value=Settings()):
        app = AppTest.from_file(ROOT / "app.py").run()
        app.session_state["procedure_result"] = {"message": "Old BG result", "country": "BG"}
        app.session_state["procedure_context"] = ["BG", "en"]
        next(s for s in app.selectbox if s.label == "Applicable country").select("DE").run()
        assert not app.exception
        assert not any("Old BG result" in m.value for m in app.markdown)


def test_bulgarian_language_switch_and_session_preservation():
    with patch("pharmaops.config.Settings.load", return_value=Settings()):
        app = AppTest.from_file(ROOT / "app.py").run()
        app.text_area[0].set_value("Existing description must survive switching.").run()
        app.selectbox(key="ui_language").select("Български").run()
        assert not app.exception
        assert any(b.label == "Намери процедура" for b in app.button)
        assert any("MOCK РЕЖИМ" in w.value for w in app.warning)
        assert app.text_area[0].value == "Existing description must survive switching."
        app.selectbox(key="ui_language").select("English").run()
        assert any(b.label == "Find procedure" for b in app.button)
