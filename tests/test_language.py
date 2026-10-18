from pharmaops.config import Settings
from pharmaops.i18n import translate
from pharmaops.providers import Provider
from pharmaops.schemas import Claim, GroundedAnswer
from pharmaops.workflow import run_workflow, verify
from tests.test_workflow import Evidence, request


def test_bulgarian_scope_and_country_rules():
    provider = Provider(Settings())
    result = run_workflow(
        provider,
        Evidence(),
        None,
        **request(question="Какво да направя при повредена опаковка?", language="bg"),
    )
    assert result["answer"].supported
    result = run_workflow(
        provider,
        Evidence(),
        None,
        **request(question="Връщане в България и Германия", language="bg"),
    )
    assert "ambiguous" in result["message"]


def test_translation_keeps_original_citation_verification():
    evidence = Evidence()
    claim = Claim(
        citation_id="valid-id",
        quote=evidence.doc.page_content,
        translation_bg="Запишете видимата повреда по опаковката.",
    )
    assert verify(GroundedAnswer(supported=True, claims=[claim]), [evidence.doc])
    assert translate("Retrieved 3 passages.", "bg") == "Извлечени откъси: 3."
    assert translate("Missing information: description", "bg") == "Липсваща информация: описание"
    assert translate("Find procedure", "en") == "Find procedure"
