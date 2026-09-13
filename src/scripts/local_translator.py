"""Tier-0 Multilingual Transcreation and Subtitle Translation Utility."""

from typing import Final

INDIAN_LANGUAGES: Final[set[str]] = {
    "te", "hi", "ta", "kn", "ml", "bn", "mr", "gu", "pa", "or", "as"
}

INDIAN_SUBTITLE_BUNDLE: Final[list[str]] = ["en", "te", "hi", "ta", "kn", "ml"]
WORLD_SUBTITLE_BUNDLE: Final[list[str]] = ["en", "es", "fr", "de", "ja", "pt"]

LANGUAGE_NAMES: Final[dict[str, str]] = {
    "en": "English",
    "te": "Telugu (తెలుగు)",
    "hi": "Hindi (हिन्दी)",
    "ta": "Tamil (தமிழ்)",
    "kn": "Kannada (ಕನ್ನಡ)",
    "ml": "Malayalam (മലയാളം)",
    "es": "Spanish (Español)",
    "fr": "French (Français)",
    "de": "German (Deutsch)",
    "ja": "Japanese (日本語)",
    "pt": "Portuguese (Português)",
}

TRANSCREATION_CORPUS: Final[list[dict[str, str]]] = [
    {
        "en": "They called it Work From Home, but we stay logged in 18 hours a day... for a 30k salary!",
        "te": "వర్క్ ఫ్రమ్ హోమ్ అని చెప్పి రోజుకి 18 గంటలు లాగిన్ లోనే ఉంటే... జీతం ఏమో నెలకి 30 వేలు!",
        "hi": "वर्क फ्रॉम होम कहकर दिन में 18 घंटे लॉगिन रहते हैं... और सैलरी वही महीने की 30 हज़ार!",
        "ta": "வொர்க் ஃப்ரம் ஹோம் என்று சொல்லி தினமும் 18 மணி நேரம் லாகின்... சம்பளம் வெறும் 30 ஆயிரம்!",
        "kn": "ವರ್ಕ್ ಫ್ರಮ್ ಹೋಮ್ ಅಂತ ಹೇಳಿ ದಿನಕ್ಕೆ 18 ಗಂಟೆ ಲಾಗಿನ್... ಸಂಬಳ ತಿಂಗಳಿಗೆ 30 ಸಾವಿರ!",
        "ml": "വർക്ക് ഫ്രം ഹോം എന്ന് പറഞ്ഞ് ദിവസവും 18 മണിക്കൂർ ലോഗിൻ... ശമ്പളം മാസം 30 ആയിരം!",
        "es": "¡Dijeron trabajo remoto, pero pasamos 18 horas al día conectados por un salario mínimo!",
        "fr": "Ils ont dit télétravail, mais on est connectés 18h par jour pour un salaire modeste !",
        "de": "Homeoffice hieß es, aber wir sind 18 Stunden am Tag eingeloggt für ein Minimalgehalt!",
        "ja": "在宅勤務と言いながら1日18時間ログイン…給料はたったの3万円！",
        "pt": "Trabalho remoto disseram eles, mas ficamos 18 horas por dia conectados por quase nada!",
    },
    {
        "en": "We have earned a PhD in lying that the WiFi died every single time the manager calls.",
        "te": "మేనేజర్ కాల్ వచ్చిన ప్రతిసారీ వైఫై కట్ అయిందని అబద్ధం చెప్పే కళ లో మనం డాక్టరేట్ చేసాం.",
        "hi": "मैनेजर की कॉल आते ही 'वाईफाई कट गया' बोलने की कला में हमने डॉक्टरेट कर रखी है।",
        "ta": "மேனேஜர் கால் வந்தாலே 'வைஃபை கட்' என்று பொய் சொல்லும் கலையில் நாம் டாக்டர் பட்டம் வாங்கிட்டோம்.",
        "kn": "ಮ್ಯಾನೇಜರ್ ಕಾಲ್ ಬಂದಾಗೆಲ್ಲ 'ವೈಫೈ ಕಟ್ ಆಯ್ತು' ಅಂತ ಸುಳ್ಳು ಹೇಳೋ ಕಲೆಯಲ್ಲಿ ನಾವೇ ಡಾಕ್ಟರೇಟ್!",
        "ml": "മാനേജർ വിളിക്കുമ്പോഴൊക്കെ 'വൈഫൈ കട്ടായി' എന്ന് കള്ളം പറയുന്നതിൽ നമ്മൾ ഡോക്ടറേറ്റെടുത്തു!",
        "es": "Tenemos un doctorado en inventar que se cayó el WiFi cada vez que llama el jefe.",
        "fr": "On a un doctorat dans l'art de prétendre que le WiFi a coupé dès que le manager appelle.",
        "de": "Wir haben einen Doktortitel darin zu behaupten, dass das WLAN abgestürzt ist, wenn der Chef anruft.",
        "ja": "マネージャーから電話が来るたびに『Wi-Fiが落ちた』と嘘をつく達人になりました。",
        "pt": "Temos doutorado em fingir que o Wi-Fi caiu toda vez que o chefe liga.",
    },
    {
        "en": "Still, staying home in pajamas beats being stuck in rush-hour traffic for hours!",
        "te": "కానీ ఆఫీస్ కి వెళ్లి ట్రాఫిక్ లో గంటలు నిలబడటం కంటే ఇంట్లోనే బెస్ట్ కదా!",
        "hi": "लेकिन ऑफिस जाकर ट्रैफिक में घंटों फंसने से तो घर पर ही रहना बेहतर है ना!",
        "ta": "ஆனாலும் ஆபீஸ் போய் டிராஃபிக்கில் மணிக்கணக்கில் நிற்பதை விட வீட்டில் இருப்பதே மேல்!",
        "kn": "ಆದ್ರೂ ಆಫೀಸ್‌ಗೆ ಹೋಗಿ ಟ್ರಾಫಿಕ್‌ನಲ್ಲಿ ಗಂಟೆಗಟ್ಟಲೆ ನಿಲ್ಲೋದಕ್ಕಿಂತ ಮನೆಯಲ್ಲೇ ಇರೋದು ಬೆಸ್ಟ್ ಅಲ್ವಾ!",
        "ml": "എങ്കിലും ഓഫീസിൽ പോയി ട്രാഫിക്കിൽ മണിക്കൂറുകൾ പെടുന്നതിലും നല്ലത് വീട്ടിലിരിക്കുന്നതല്ലേ!",
        "es": "¡Aun ایسے, quedarse en casa en pijama es mil veces mejor que el tráfico diario!",
        "fr": "Mais bon, rester en pyjama chez soi reste mille fois mieux que les embouteillages !",
        "de": "Trotzdem: Zu Hause im Schlafanzug ist tausendmal besser als stundenlanger Berufsverkehr!",
        "ja": "それでも、何時間も渋滞に巻き込まれるよりパジャマで家にいる方がマシですよね！",
        "pt": "Ainda assim, ficar em casa de pijama é muito melhor do que horas no trânsito!",
    },
]


def is_indian_language(lang_code: str) -> bool:
    """Determine if a language code belongs to the Indian linguistic family."""
    clean = lang_code.split("-")[0].lower()
    return clean in INDIAN_LANGUAGES


def get_subtitle_bundle_languages(primary_language: str) -> list[str]:
    """Get the appropriate 5-6 subtitle languages based on content region."""
    if is_indian_language(primary_language):
        return list(INDIAN_SUBTITLE_BUNDLE)
    return list(WORLD_SUBTITLE_BUNDLE)


def translate_dialogue(text: str, source_lang: str, target_lang: str) -> str:
    """Translate or transcreate a dialogue segment into the target language."""
    src = source_lang.split("-")[0].lower()
    tgt = target_lang.split("-")[0].lower()

    if src == tgt:
        return text

    # Check corpus for exact or partial transcreation match
    clean_text = text.strip()
    for entry in TRANSCREATION_CORPUS:
        src_val = entry.get(src, "").strip()
        tgt_val = entry.get(tgt, "").strip()
        if src_val and tgt_val:
            if src_val in clean_text or clean_text in src_val:
                return tgt_val

    # Default fallback: return original text with language tag if no transcreation exists
    return f"[{tgt.upper()}] {clean_text}"
