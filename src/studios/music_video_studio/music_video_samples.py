"""Multilingual lyrics and title samples for offline mock and fallback generation."""

from __future__ import annotations
from typing import Any

OFFLINE_LANG_SAMPLES: dict[str, dict[str, str]] = {
    "te": {
        "title_en": "Manchu Kurise Vela",
        "title_localized": "మంచు కురిసే వేళ (Manchu Kurise Vela)",
        "lyrics": "పల్లవి:\nమంచు కురిసే వేళలోన మనసు నిన్నే కోరింది.\nచరణం:\nగుండెలోన ప్రేమ రాగం నిత్యం మ్రోగుతున్నది.",
        "s1": "మంచు కురిసే వేళలోన",
        "s1_en": "Manchu kurise velalona | In the falling mist",
        "s2": "గుండెలోన ప్రేమ రాగం",
        "s2_en": "Gundelona prema raagam | Melody in my heart",
    },
    "hi": {
        "title_en": "Khwabon Ki Wadiyon Mein",
        "title_localized": "ख्वाबों की वादियों में (Khwabon Ki Wadiyon)",
        "lyrics": "मुखड़ा:\nख्वाबों की वादियों में तेरी ही सदा है।\nअंतरा:\nसांसों की हर लय पर तेरा ही नाम लिखा है।",
        "s1": "ख्वाबों की वादियों में",
        "s1_en": "Khwabon ki wadiyon mein | In the valley of dreams",
        "s2": "सांसों की हर लय पर",
        "s2_en": "Saanson ki har lay par | On the rhythm of breath",
    },
    "mr": {
        "title_en": "Man Udhan Varyache",
        "title_localized": "मन उधाण वाऱ्याचे (Man Udhan Varyache)",
        "lyrics": "ध्रुवपद:\nमन उधाण वाऱ्याचे सुरांच्या हिंदोळ्यावर झुलते.\nकडवे:\nसांजवेळेस आठवणींचे दीप हृदयात उजळते.",
        "s1": "मन उधाण वाऱ्याचे",
        "s1_en": "Man udhan varyache | Restless breeze of the soul",
        "s2": "सांजवेळेस आठवणींचे दीप",
        "s2_en": "Sanjveles aathwaninche deep | Lamps of memory at dusk",
    },
    "bn": {
        "title_en": "Tomar Khonje Mon",
        "title_localized": "তোমার খোঁজে মন (Tomar Khonje Mon)",
        "lyrics": "স্থায়ী:\nতোমার খোঁজে মন যে হারায় সুরের মোহনায়।\nঅন্তরা:\nহৃদয় মাঝে প্রেম জাগে নদীর ঠিকানায়।",
        "s1": "তোমার খোঁজে মন যে হারায়",
        "s1_en": "Tomar khonje mon je haray | Lost searching for you",
        "s2": "হৃদয় মাঝে প্রেম জাগে",
        "s2_en": "Hridoy majhe prem jaage | Love awakens by the river",
    },
    "or": {
        "title_en": "E Mana Mo Chhanchhala",
        "title_localized": "ଏ ମନ ମୋ ଚଞ୍ଚଳ (E Mana Mo Chhanchhala)",
        "lyrics": "ଘୋଷା:\nଏ ମନ ମୋ ଚଞ୍ଚଳ ତୁମ ପ୍ରେମ ବଇଁଶୀ ସୁରେ।\nଅନ୍ତରା:\nନୀଳ ଜଳଧି ତଟେ ଝୁରେ ହୃଦୟ ମୋହନ ରୂପେ।",
        "s1": "ଏ ମନ ମୋ ଚଞ୍ଚଳ",
        "s1_en": "E mana mo chhanchhala | My restless heart",
        "s2": "ତୁମ ପ୍ରେମ ବଇଁଶୀ ସୁରେ",
        "s2_en": "Tuma prema bainsi sure | In flute notes of love",
    },
    "ks": {
        "title_en": "Roshche Roz Roz",
        "title_localized": "روش چھہ روز روز (Roshche Roz Roz)",
        "lyrics": "مکھڑا:\nروش چھہ روز روز چانی دوری ستائیوم۔\nانترہ:\nپامپور چہ گلابو منز چونی تصویر لبیوم।",
        "s1": "روش چھہ روز روز",
        "s1_en": "Roshche roz roz | Stay a little longer",
        "s2": "پامپور چہ گلابو منز",
        "s2_en": "Pampore che gulabo manz | Among the saffron blooms",
    },
    "sd": {
        "title_en": "Muhinji Hojamalo",
        "title_localized": "منهنجي هوجمالو (Muhinji Hojamalo)",
        "lyrics": "مکھڙو:\nمنهنجي هوجمالو سنڌوءَ جي ڇولين ۾ سڏ ڪري۔\nانترو:\nجهوليلال جي رحمت سدا اسان تي رهندي۔",
        "s1": "منهنجي هوجمالو",
        "s1_en": "Muhinji Hojamalo | Celebration by the Indus",
        "s2": "سنڌوءَ جي ڇولين ۾",
        "s2_en": "Sindhu-a ji chholiyan mein | In the waves of the river",
    },
    "gu": {
        "title_en": "Mor Bani Thanghat Kare",
        "title_localized": "મોર બની થનગનાટ કરે (Mor Bani Thanghat)",
        "lyrics": "ધ્રુવ:\nમોર બની થનગનાટ કરે મન મારું વર્ષાઋતુમાં.\nઅંતરો:\nપ્રીતની પંખી ઊડે ગગને હૈયાના ગીતો ગાતાં.",
        "s1": "મોર બની થનગનાટ કરે",
        "s1_en": "Mor bani thanghat kare | Heart dances like a peacock",
        "s2": "પ્રીતની પંખી ઊડે ગગને",
        "s2_en": "Preet ni pankhi ude | Birds of love in flight",
    },
    "pa": {
        "title_en": "Ishq Di Mehak",
        "title_localized": "ਇਸ਼ਕ ਦੀ ਮਹਿਕ (Ishq Di Mehak)",
        "lyrics": "ਮੁਖੜਾ:\nਇਸ਼ਕ ਦੀ ਮਹਿਕ ਨਾਲ ਮਹਿਕਿਆ ਸਾਰਾ ਜਹਾਨ ਵੇ।\nਅੰਤਰਾ:\nਤੇਰੇ ਬਿਨਾ ਸੁੰਨਾ ਲੱਗਦਾ ਸਾਡਾ ਹਰ ਅਰਮਾਨ ਵੇ।",
        "s1": "ਇਸ਼ਕ ਦੀ ਮਹਿਕ ਨਾਲ",
        "s1_en": "Ishq di mehak naal | Fragrance of true love",
        "s2": "ਤੇਰੇ ਬਿਨਾ ਸੁੰਨਾ ਲੱਗਦਾ",
        "s2_en": "Tere bina sunna lagda | Empty without you",
    },
    "ja": {
        "title_en": "Sakura Mau Kisetsu",
        "title_localized": "桜舞う季節 (Sakura Mau Kisetsu)",
        "lyrics": "Aメロ:\n桜舞う季節に風が優しく囁く。\nサビ:\n君の手を握りしめて永遠を誓うよ。",
        "s1": "桜舞う季節に風が囁く",
        "s1_en": "Sakura mau kisetsu ni | Wind whispers in sakura season",
        "s2": "君の手を握りしめて",
        "s2_en": "Kimi no te wo nigirishimete | Holding your hand tight",
    },
    "ko": {
        "title_en": "Gyeoulbamui Chueok",
        "title_localized": "겨울밤의 추억 (Gyeoulbamui Chueok)",
        "lyrics": "Verse 1:\n겨울밤 하얀 눈이 내려와 우리 기억을 덮네.\nChorus:\n언제ナ 내 곁에 머물러준 너에게 감사해.",
        "s1": "겨울밤 하얀 눈이 내려와",
        "s1_en": "Gyeoulbam hayan nuni naeryeowa | White snow falls",
        "s2": "언제나 내 곁에 머물러줘",
        "s2_en": "Eonjena nae gyeote meomulleojwo | Stay by my side",
    },
    "fr": {
        "title_en": "Sous Le Ciel De Paris",
        "title_localized": "Sous Le Ciel De Paris",
        "lyrics": "Couplet 1:\nSous le ciel de Paris la Seine murmure notre histoire.\nRefrain:\nUn doux baiser dans la brume du soir l'amour nous attend.",
        "s1": "Sous le ciel de Paris",
        "s1_en": "Sous le ciel de Paris | Under Paris skies",
        "s2": "Un doux baiser dans la brume",
        "s2_en": "Un doux baiser dans la brume | Gentle evening kiss",
    },
    "es": {
        "title_en": "Bajo La Luz De La Luna",
        "title_localized": "Bajo La Luz De La Luna",
        "lyrics": "Verso 1:\nBajo la suave luz de la luna tu mirada ilumina mi alma.\nCoro:\nBailamos al compás de la brisa marina corazón en calma.",
        "s1": "Bajo la suave luz de la luna",
        "s1_en": "Bajo la luz de la luna | Under the moonlight",
        "s2": "Bailamos al compás del mar",
        "s2_en": "Bailamos al compás del mar | Dancing to the sea",
    },
}


def get_multilingual_sample_lyrics(language: str, country: str) -> dict[str, str]:
    """Retrieve authentic multilingual lyric and subtitle sample for target language."""
    lang_k = (language or "en").lower()
    return OFFLINE_LANG_SAMPLES.get(
        lang_k,
        {
            "title_en": f"{country} Melody in {lang_k.upper()}",
            "title_localized": f"{country} Melody ({lang_k.upper()})",
            "lyrics": f"Verse 1:\nSoulful {language} melodies echoing across mountains.\nHook:\nHeartbeats in harmony timeless love.",
            "s1": f"Soulful melody in {language}",
            "s1_en": f"Soulful melody in {language} | Eternal melody",
            "s2": "Heartbeats in harmony",
            "s2_en": "Heartbeats in harmony | Timeless love",
        },
    )

__all__ = ["OFFLINE_LANG_SAMPLES", "get_multilingual_sample_lyrics"]
