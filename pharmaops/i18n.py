"""Small explicit English/Bulgarian UI catalog; source documents retain their original text."""

import re

BG = {
    "Proof of Concept (PoC) · Synthetic pharmaceutical distribution data": "Proof of Concept (PoC) · Синтетични данни за фармацевтична дистрибуция",
    "Procedure header is invalid. Inspect it and republish the seed.": "Заглавната част на процедурата е невалидна. Прегледайте я и качете отново оригинала.",
    "Document storage": "Хранилище за документи",
    "Fictional procedure library": "Библиотека с измислени процедури",
    "LOCAL AZURITE EMULATOR · Azure Blob SDK · No Azure account or subscription": "ЛОКАЛЕН AZURITE ЕМУЛАТОР · Azure Blob SDK · Без Azure акаунт или абонамент",
    "Publish the seven seeded procedures, inspect metadata, and download verified originals.": "Качете седемте примерни процедури, разгледайте метаданните и изтеглете проверени оригинали.",
    "This library is a storage exercise. Procedure answers still use the local indexed corpus.": "Библиотеката е упражнение за съхранение. Отговорите по процедури използват локалния индексиран корпус.",
    "Contacting local procedure storage…": "Свързване с локалното хранилище…",
    "Publish demo procedures": "Качи примерните процедури",
    "Demo procedures published to local storage.": "Примерните процедури са качени в локалното хранилище.",
    "Refresh stored procedures": "Обнови списъка с процедури",
    "No procedures loaded. Start Azurite, then publish or refresh.": "Няма заредени процедури. Стартирайте Azurite, после качете или обновете списъка.",
    "Stored procedure": "Съхранена процедура",
    "Prepare verified download": "Подготви проверено изтегляне",
    "Download original procedure": "Изтегли оригиналната процедура",
    "SHA-256 and document metadata checked. Original English source.": "Проверени SHA-256 и метаданни. Оригинален английски източник.",
    "No seeded fictional procedures found.": "Няма намерени примерни измислени процедури.",
    "A seeded procedure exceeds the 256 KB demo limit.": "Примерна процедура надвишава демонстрационния лимит от 256 KB.",
    "Publishing failed. Start local Azurite on port 10000 and retry. Some files may already be stored; publishing again safely replaces the same names.": "Качването не успя. Стартирайте локалния Azurite на порт 10000 и повторете. Някои файлове може вече да са записани; повторното качване заменя същите имена.",
    "Storage listing exceeds the demo limit of 100 objects.": "Списъкът надвишава демонстрационния лимит от 100 обекта.",
    "Procedure storage unavailable or invalid. Start Azurite and publish the demo procedures.": "Хранилището е недостъпно или невалидно. Стартирайте Azurite и качете примерните процедури.",
    "Choose one of the seeded procedure filenames; arbitrary paths are not allowed.": "Изберете име от примерните процедури; произволни пътища не са разрешени.",
    "Stored procedure exceeds the demo size limit.": "Съхранената процедура надвишава демонстрационния лимит за размер.",
    "Stored procedure integrity check failed. Inspect it and republish the seed.": "Проверката на съхранената процедура е неуспешна. Прегледайте я и качете отново оригинала.",
    "Download failed. Check Azurite and republish the fictional procedure.": "Изтеглянето не успя. Проверете Azurite и качете отново измислената процедура.",
    "Distribution Support Assistant": "Асистент за дистрибуционни операции",
    "Find procedure evidence and prepare delivery complaints.": "Намерете процедури и подгответе оплаквания за доставки.",
    "LOCAL DEMO · FICTIONAL DATA · Independent portfolio project · Illustrative procedures only": "ЛОКАЛНО ДЕМО · ИЗМИСЛЕНИ ДАННИ · Независим портфолио проект · Примерни процедури",
    "Model mode": "Режим на модела",
    "Local semantic embeddings": "Локални семантични embeddings",
    "MOCK MODE — deterministic simulated responses. No real LLM is running.": "MOCK РЕЖИМ — симулирани отговори по фиксирани правила. Не се използва реален LLM.",
    "Applicable country": "Държава на доставката",
    "Choose country": "Изберете държава",
    "Workspace": "Работно пространство",
    "Provider": "Доставчик на модела",
    "Model": "Модел",
    "Model calls are sent to the configured provider. Use fictional information only.": "Заявките към модела се изпращат до избрания доставчик. Използвайте само измислена информация.",
    "Complaint country is checked against the delivery record. No production authentication.": "Държавата се проверява спрямо записа за доставката. Демото няма система за вход.",
    "Demo delivery": "Примерна доставка",
    "Bulgaria": "България",
    "Services and the business API are local. The API represents a simulated external system.": "Услугите и бизнес API работят локално. API симулира външна бизнес система.",
    "Checking delivery procedures…": "Проверка на процедурите за доставки…",
    "The workflow could not complete. Check configuration and retry. No complaint was submitted by the workflow.": "Процесът не завърши. Проверете настройките и опитайте отново. Процесът не е подал оплакване.",
    "Source": "Източник",
    "Activity": "Действия",
    "Effective": "В сила от",
    "Procedure questions": "Въпроси за процедури",
    "Delivery complaints": "Оплаквания за доставки",
    "Find the next operational step": "Намерете следващата оперативна стъпка",
    "Your procedure question": "Вашият въпрос за процедура",
    "What should I do if a delivery arrives with damaged outer packaging?": "Какво да направя, ако доставка пристигне с повредена външна опаковка?",
    "Find procedure": "Намери процедура",
    "Prepare → review → confirm": "Подготовка → преглед → потвърждение",
    "The assistant can save a draft. Only your confirmation button submits it to the simulated API.": "Асистентът може да запази чернова. Само вашето потвърждение я подава към симулирания API.",
    "Delivery identifier": "Номер на доставка",
    "Complaint category": "Категория на оплакването",
    "Factual description (required, 10–1,500 characters)": "Описание на фактите (задължително, 10–1500 знака)",
    "Describe the visible issue and any relevant counts.": "Опишете видимия проблем и съответните количества.",
    "Affected packages": "Засегнати пакети",
    "Requested resolution": "Желано решение",
    "No emails are sent. Recording a complaint does not authorize returns or replacement stock.": "Не се изпращат имейли. Записването на оплакване не разрешава връщане или замяна на стока.",
    "Prepare / update draft": "Подготви / обнови чернова",
    "Draft preview": "Преглед на черновата",
    "Fields changed. Update the draft and review it again before confirming.": "Полетата са променени. Обновете черновата и я прегледайте отново преди потвърждение.",
    "I reviewed this exact draft and confirm submission to the simulated API.": "Прегледах точно тази чернова и потвърждавам подаването към симулирания API.",
    "Confirm and submit complaint": "Потвърди и подай оплакването",
    "Complaint recorded": "Оплакването е записано",
    "This draft was already submitted. The same reference was returned.": "Тази чернова вече е подадена. Върнат е същият референтен номер.",
    "Start a new complaint": "Ново оплакване",
    "Original English source excerpt": "Оригинален английски откъс",
    "Machine translation; verify against the original source.": "Машинен превод; проверете спрямо оригиналния източник.",
    "Source procedures are fictional and written in English.": "Източниците са измислени процедури, написани на английски.",
    "damaged_packaging": "Повредена опаковка",
    "missing_items": "Липсващи артикули",
    "discrepancy": "Несъответствие",
    "return_request": "Заявка за връщане",
    "investigation": "Проверка на случая",
    "replacement_review": "Преглед за замяна",
    "return_review": "Преглед за връщане",
    "The available procedures do not support an answer to this question.": "Наличните процедури не съдържат достатъчно информация за отговор на този въпрос.",
    "Evidence-backed procedure excerpts:": "Откъси от приложимите процедури:",
    "Use at most 1,500 characters.": "Използвайте най-много 1500 знака.",
    "I cover fictional distribution procedures and complaints. I cannot provide medical advice or answer unrelated questions.": "Помагам с измислени дистрибуционни процедури и оплаквания. Не давам медицински съвети или отговори извън тази област.",
    "Choose one country (BG, DE, or RO) to select applicable procedures.": "Изберете една държава (BG, DE или RO), за да намерите приложимите процедури.",
    "Country is ambiguous. Select one country matching your question.": "Държавата е неясна. Изберете една държава, която съответства на въпроса.",
    "Review the delivery ID, description (10–1,500 characters), category, and package count.": "Проверете номера на доставката, описанието (10–1500 знака), категорията и броя пакети.",
    "Tool limit reached. Refine your request and retry.": "Достигнат е лимитът на действията. Уточнете заявката и опитайте отново.",
    "Model requested a disallowed tool. No action taken.": "Моделът поиска неразрешен инструмент. Не е извършено действие.",
    "Please clarify the delivery issue and required fields.": "Уточнете проблема с доставката и задължителните полета.",
    "Review the draft. Submission requires your explicit confirmation.": "Прегледайте черновата. Подаването изисква вашето изрично потвърждение.",
    "Draft validation failed.": "Проверката на черновата е неуспешна.",
    "Model unavailable, rate limited, or returned an invalid response. Check the provider/model and retry. No mock fallback was used.": "Моделът е недостъпен, ограничен или е върнал невалиден отговор. Проверете доставчика и модела и опитайте отново. Не е използван mock заместител.",
    "Provider quota reached. Wait before retrying; the Free plan has rate limits. No mock or paid fallback was used.": "Достигнат е лимитът на доставчика. Изчакайте преди нов опит; безплатният план има ограничения. Не е използван mock или платен заместител.",
    "GROQ_API_KEY is missing. Set it in .env or choose mock mode.": "Липсва GROQ_API_KEY. Попълнете го в .env или изберете mock режим.",
    "Index missing. Run: uv run python -m pharmaops.cli index": "Липсва индекс. Изпълнете: uv run python -m pharmaops.cli index",
    "Embedding model changed. Rebuild the index first.": "Моделът за embeddings е променен. Първо изградете индекса отново.",
    "Choose one country: BG, DE, or RO.": "Изберете една държава: BG, DE или RO.",
    "Semantic retrieval failed. Rebuild the local index and retry.": "Семантичното търсене не успя. Изградете локалния индекс отново и повторете.",
    "Delivery or draft not found. Check the identifier.": "Доставката или черновата не е намерена. Проверете номера.",
    "Draft changed or was already submitted. Review it again.": "Черновата е променена или вече е подадена. Прегледайте я отново.",
    "Required fields do not match the delivery. Review your draft.": "Задължителните полета не съответстват на доставката. Проверете черновата.",
    "Simulated business API unavailable or invalid. Start the API and retry; an interrupted submission can safely be retried.": "Симулираният бизнес API е недостъпен или невалиден. Стартирайте API и повторете; прекъснато подаване може безопасно да се повтори.",
    "Excluded suspicious document instructions.": "Изключени са подозрителни инструкции в документ.",
    "Draft ready for review.": "Черновата е готова за преглед.",
    "Knowledge agent selected evidence.": "Агентът за знания избра подкрепящи откъси.",
    "Verification withheld an unsupported answer.": "Проверката спря неподкрепен от източниците отговор.",
    "Verified citation IDs and exact supporting excerpts.": "Проверени са цитатите и точните подкрепящи откъси.",
    "Coordinator selected the procedure workflow.": "Координаторът избра процеса за въпроси по процедури.",
    "Coordinator selected the complaint workflow.": "Координаторът избра процеса за оплаквания.",
    "delivery_id": "номер на доставка",
    "category": "категория",
    "description": "описание",
    "affected_packages": "засегнати пакети",
    "requested_resolution": "желано решение",
    "country": "държава",
    "draft_id": "номер на чернова",
    "revision": "версия",
    "source_ids": "източници",
}


def translate(text: str, language="en") -> str:
    if language != "bg":
        return text
    if text in BG:
        return BG[text]
    if match := re.fullmatch(r"Retrieved (\d+) passages\.", text):
        return f"Извлечени откъси: {match[1]}."
    if match := re.fullmatch(r"Found delivery (DEL-\d{4})\.", text):
        return f"Намерена доставка {match[1]}."
    for prefix, replacement in [
        ("Missing information: ", "Липсваща информация: "),
        ("Complete required complaint fields: ", "Попълнете задължителните полета: "),
    ]:
        if text.startswith(prefix):
            fields = text[len(prefix) :].split(", ")
            return replacement + ", ".join(BG.get(f, f) for f in fields)
    if text.startswith("Selected country does not match delivery. Choose "):
        country = re.search(r"Choose (BG|DE|RO)", text)[1]
        return f"Избраната държава не съответства на доставката. Изберете {country} и подгответе отново."
    if text.startswith("Local embedding model unavailable."):
        return (
            "Локалният модел за embeddings е недостъпен. Първото изграждане на индекса изисква "
            "интернет за изтегляне на малкия FastEmbed модел. Повторете командата при връзка."
        )
    return text
