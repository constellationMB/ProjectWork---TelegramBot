import requests
import spacy
from openai import OpenAI
from loguru import logger

from configuration import settings

LANGUAGETOOL_API_URL = "https://api.languagetool.org/v2/check"


def rename(text: str) -> str:
    tag_mapping = {
        'PRON': 'Местоимение',
        'NOUN': 'Существительное',
        'PROPN': 'Собственное существительное',
        'ADJ': 'Прилагательное',
        'ADV': 'Наречие',
        'VERB': 'Глагол',
        'AUX': 'Вспомогательный глагол',
        'ADP': 'Предлог',
        'NUM': 'Числительное',
        'DET': 'Артикль',
        'PART': 'Частица',
        'SYM': 'Символ',
        'INTJ': 'Междометие',
        'PUNCT': 'Знак препинания',
        'X': 'Прочее',
        'CCONJ': 'Союз',
        'SCONJ': 'Субстантивированный союз',
    }

    return tag_mapping.get(text, text)


def check_text_with_languagetool(text: str) -> list:
    try:
        payload = {
            'text': text,
            'language': 'ru'
        }
        response = requests.post(LANGUAGETOOL_API_URL, data=payload)
        result = response.json()

        if 'matches' not in result or len(result['matches']) == 0:
            return ["<b>Ошибки отсутствуют ✅🎉</b>", False]

        corrections = []
        for i, match in enumerate(result['matches'], start=1):
            message = (
                f"<b>— — — — — —</b>"
                f"✨ <b>Ошибка #{i}</b>\n"
                f"🔍 <b>Тип:</b> {match['shortMessage'] or 'Не указано'}\n"
                f"📋 <b>Описание:</b> {match['message']}\n"
                f"📖 <b>Правило:</b> {match['rule']['description']}\n"
                f"✏️ <b>Контекст:</b> {match['context']['text']}\n"
                f"➡️ <b>Рекомендуемое исправление:</b> "
                f"{', '.join([m['value'] for m in match['replacements'][:3]]) if match['replacements'] else 'Не найдено / Отсутствует'}\n"
            )
            corrections.append(message)

        return ["\n\n".join(corrections), True]

    except Exception as e:
        logger.warning(f"⚠️ Не удалось проверить текст с помощью LanguageTool: {e}")
        return ["⚠️ А его нет, LanguageTool недоступен (ʘ ͟ʖ ʘ)", False]


def check_and_improve_with_languagetool(text: str) -> str:
    url = "https://api.languagetool.org/v2/check"
    payload = {
        "text": text,
        "language": "ru"
    }

    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
        matches = response.json().get("matches", [])

        if not matches:
            return "🎉 Текст не содержит ошибок или улучшений не требуется."

        corrected_text = text
        explanations = []

        for match in matches:
            start = match["offset"]
            end = start + match["length"]
            replacement = match["replacements"][0]["value"] if match["replacements"] else None
            if replacement:
                corrected_text = corrected_text[:start] + replacement + corrected_text[end:]
                explanations.append(f"🔄 {text[start:end]} → {replacement}: {match['message']}")

        return f"✨ Исправленный текст: {corrected_text}\n\n📋 Пояснения:\n" + "\n".join(explanations)

    except:
        logger.warning("⚠️ Не удалось проверить текст с помощью API LanguageTool")
        return "⚠️ А её нет, LanguageTool сломался ＞︿＜"


def check_text_with_spacy(text: str) -> str:
    try:
        nlp = spacy.load("ru_core_news_sm")
        doc = nlp(text)
        sentences = list(doc.sents)

        results = []
        for sentence in sentences:
            sentence_result = []
            for token in sentence:
                if token.is_punct or token.is_space:
                    continue
                sentence_result.append(f"🔹 {token.text} - {rename(token.pos_)}")
            results.append("\n".join(sentence_result))

        return "📝 Результаты анализа:\n\n" + "\n\n".join(results)

    except:
        logger.warning("⚠️ Не удалось проверить текст с помощью SpaCy")
        return "⚠️ А его нет, SpaCy приказал жить долго <( _ _ )>"


def check_text_with_openai(text: str, model: str = "gpt-3.5-turbo", max_tokens: int = 200) -> str:
    try:
        client = OpenAI(api_key=settings.CHAT_GPT_TOKEN)

        response = client.completions.create(
            model=model,
            prompt=[
                "Твоя задача - при получении запроса от пользователя в виде текста, проверить его на ошибки и исправить их, если они имеются. "
                "Так же, если это предложение, то предложи свою перефразировку, если она нужна. "
                "Если есть ошибки в построении, исправляй. Каждую ошибку кратко поясняй.",
                text
            ],
            max_tokens=max_tokens,
            temperature=0.5
        )

        return f"✨ Ответ ChatGPT:\n\n{response.choices[0].message.content}"

    except:
        logger.warning("⚠️ Не удалось проверить текст с помощью ChatGPT")
        return "⚠️ А его нет, ChatGPT в России заблокирован ಥ_ಥ"
