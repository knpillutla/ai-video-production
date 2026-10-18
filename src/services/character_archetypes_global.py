"""Catalog of Global International Character Archetypes (Japanese, French, Spanish, Korean, Western)."""

from __future__ import annotations
from src.services.character_archetype_catalog import ArchetypeSpec

# Japanese Character Archetypes (ja) - Refined almond monolid/soft double eyelid, smooth jawline, porcelain/warm ivory skin, sleek glossy black hair
JAPANESE_FEMALE_ARCHETYPES: list[ArchetypeSpec] = [
    ArchetypeSpec("Sakura", 23, "delicate almond eyes, refined heart-shaped jawline", "sleek glossy black bob with airy curtain bangs", "luminous porcelain-ivory skin", "cherry blossom pink and ivory", 10007),
    ArchetypeSpec("Aoi", 24, "serene doe eyes, graceful cheekbones, gentle smile", "waist-length silky raven hair with soft curve", "clear warm ivory complexion", "indigo blue and champagne", 20011),
    ArchetypeSpec("Yuna", 24, "sparkling expressive dark eyes, delicate chin", "textured shoulder-length wavy lob", "radiant peach-ivory skin", "matcha green and cream", 30013),
    ArchetypeSpec("Mei", 23, "sweet charming smile, refined soft facial contours", "straight black tresses with neat fringe", "glowing porcelain skin tone", "plum purple and pearl", 40017),
    ArchetypeSpec("Hinata", 25, "striking feline eyes, high sculpted cheekbones", "voluminous layered dark waves", "sun-kissed warm ivory complexion", "terracotta and charcoal", 50021),
    ArchetypeSpec("Nanami", 24, "captivating serene gaze, elegant slender jaw", "low sleek chignon with minimalist wooden pin", "clear porcelain-honey skin", "crimson scarlet and sand", 60029),
    ArchetypeSpec("Riko", 23, "youthful radiance, bright cheerful almond eyes", "feathered modern layered cut", "radiant warm ivory skin", "powder blue and ivory", 70033),
    ArchetypeSpec("Akari", 25, "poetic introspective eyes, graceful neckline", "side-parted glossy straight hair", "glowing porcelain tone", "amber gold and navy", 80039),
    ArchetypeSpec("Hana", 24, "gentle dimpled smile, delicate defined features", "soft natural waves cascading over shoulders", "clear ivory complexion", "dusty rose and charcoal", 90047),
    ArchetypeSpec("Koharu", 25, "refined classical beauty, deep dark gaze", "smooth dark raven ponytail with clean edges", "porcelain-ivory radiant skin", "midnight navy and silver", 100051),
]

JAPANESE_MALE_ARCHETYPES: list[ArchetypeSpec] = [
    ArchetypeSpec("Haruto", 25, "sharp chiseled jawline, deep focused almond eyes", "textured modern crop with soft fringe, clean-shaven", "clear warm ivory skin", "charcoal and ivory", 15017),
    ArchetypeSpec("Ren", 24, "refined bone structure, gentle charismatic smile", "stylish naturally wavy curtain hair, clean-shaven", "porcelain-fair skin tone", "navy and camel", 25021),
    ArchetypeSpec("Kaito", 26, "athletic lean build, strong angular jaw, dark gaze", "short tapered fade with textured top, light stubble", "warm ivory masculine complexion", "forest green and black", 35027),
    ArchetypeSpec("Daiki", 25, "broad-shouldered fit frame, confident warm gaze", "classic gentleman's side-part, clean-shaven", "clear golden-ivory skin", "cobalt blue and grey", 45031),
    ArchetypeSpec("Sora", 24, "slender athletic frame, bright expressive eyes", "modern textured messy quiff, clean-shaven", "radiant porcelain-ivory skin", "espresso and champagne", 55037),
    ArchetypeSpec("Ryota", 26, "sharp defined cheekbones, intense thoughtful gaze", "slicked-back textured dark hair, subtle stubble", "sun-warmed ivory tone", "slate grey and burgundy", 65041),
    ArchetypeSpec("Kazuki", 25, "approachable warm smile, sculpted athletic chin", "tapered clean-cut sides with wavy top", "clear ivory complexion", "dark olive and oatmeal", 75047),
    ArchetypeSpec("Shota", 24, "youthful energetic poise, sharp model jawline", "feathered textured layered cut, clean-shaven", "glowing porcelain skin", "royal blue and tan", 85053),
    ArchetypeSpec("Yuto", 26, "commanding dignified presence, sharp cheekbones", "short textured crew cut, clean-shaven", "warm ivory skin tone", "deep wine and charcoal", 95059),
    ArchetypeSpec("Kenji", 27, "rugged chiseled jaw, focused intense dark eyes", "natural wavy pompadour, neat light stubble", "rich warm ivory complexion", "terracotta and cream", 105067),
]

# French Character Archetypes (fr) - Subtle Roman/Grecian nose, hazel or green/blue eyes, defined cheekbones, effortless wavy brunette or honey-blonde hair
FRENCH_FEMALE_ARCHETYPES: list[ArchetypeSpec] = [
    ArchetypeSpec("Camille", 24, "subtle sculpted Roman nose, expressive hazel-green eyes", "effortless tousled wavy brunette lob", "warm fair glowing skin", "parisian navy and cream", 10007),
    ArchetypeSpec("Juliette", 23, "delicate heart-shaped face, soft almond brown eyes", "center-parted natural honey-blonde waves", "clear porcelain complexion", "bordeaux wine and ivory", 20011),
    ArchetypeSpec("Chloe", 25, "high cheekbones, captivating serene gaze", "shoulder-length dark brown hair with curtain bangs", "sun-kissed warm golden skin", "sage green and sand", 30013),
    ArchetypeSpec("Lea", 24, "refined jawline, radiant smile, bright blue-grey eyes", "chic textured French bob", "radiant peach-fair skin", "terracotta and pearl", 40017),
    ArchetypeSpec("Manon", 25, "poetic introspective eyes, elegant slender chin", "loose romantic low bun with wispy tendrils", "clear fair-ivory tone", "powder blue and espresso", 50021),
    ArchetypeSpec("Ines", 23, "expressive almond eyes, cute dimpled smile", "voluminous natural wavy chestnut hair", "warm honey-fair complexion", "mustard amber and charcoal", 60029),
    ArchetypeSpec("Mathilde", 26, "commanding Parisian elegance, sharp cheekbones", "sleek straight dark brown hair with blunt cut", "porcelain-fair skin", "midnight black and champagne", 70033),
    ArchetypeSpec("Clementine", 24, "sweet charming demeanor, sparkling hazel eyes", "layered bouncy honey-tinted waves", "radiant fair skin", "dusty rose and camel", 80039),
    ArchetypeSpec("Louise", 25, "dignified classical beauty, deep green eyes", "elegant side-swept soft brunette waves", "clear golden-fair complexion", "forest pine and ivory", 90047),
    ArchetypeSpec("Emma", 24, "sharp modern features, captivating dark blue gaze", "modern textured wavy lob with highlights", "sun-warmed fair skin", "coral rust and cream", 100051),
]

FRENCH_MALE_ARCHETYPES: list[ArchetypeSpec] = [
    ArchetypeSpec("Antoine", 26, "chiseled square jawline, intense green-hazel eyes", "tapered naturally wavy dark brown hair, light stubble", "warm fair skin", "navy blue and oatmeal", 15017),
    ArchetypeSpec("Julien", 25, "sculpted angular cheekbones, warm brown eyes", "classic French textured crop, clean-shaven", "clear fair-golden skin", "charcoal and burgundy", 25021),
    ArchetypeSpec("Alexandre", 27, "commanding Parisian presence, sharp defined chin", "slicked-back dark chestnut hair, neat stubble", "sun-warmed fair complexion", "dark olive and cream", 35027),
    ArchetypeSpec("Maxime", 25, "athletic lean runner's frame, bright blue eyes", "modern curtain fringe haircut, clean-shaven", "radiant fair skin tone", "espresso and champagne", 45031),
    ArchetypeSpec("Lucas", 24, "slender athletic build, gentle charismatic smile", "textured wavy dark blonde locks, light stubble", "clear porcelain-fair skin", "cobalt blue and grey", 55037),
    ArchetypeSpec("Thomas", 26, "broad-shouldered fit frame, deep-set hazel eyes", "short gentleman's taper, neat short beard", "warm fair-golden complexion", "forest green and black", 65041),
    ArchetypeSpec("Gabriel", 25, "refined model bone structure, intense dark eyes", "stylish pompadour with tapered sides, clean-shaven", "fair-ivory clear skin", "maroon and sand", 75047),
    ArchetypeSpec("Hugo", 24, "youthful energetic charm, sparkling grey-blue eyes", "modern textured messy fringe, light shadow stubble", "radiant fair skin", "slate blue and camel", 85053),
    ArchetypeSpec("Theo", 26, "sharp defined jaw, warm engaging expression", "classic comb-over with clean part, clean-shaven", "sun-kissed fair complexion", "rust terracotta and navy", 95059),
    ArchetypeSpec("Pierre", 27, "dignified handsome features, focused hazel gaze", "natural wavy locks swept naturally, trimmed beard", "rich fair-golden skin", "chocolate and cream", 105067),
]

# Spanish / Latin Character Archetypes (es) - Warm olive/sun-kissed complexion, dark intense expressive almond eyes, sculpted jawline, rich dark wavy hair
SPANISH_FEMALE_ARCHETYPES: list[ArchetypeSpec] = [
    ArchetypeSpec("Lucia", 24, "striking feline dark eyes, sculpted high cheekbones", "voluminous cascading dark raven waves", "warm golden-olive glowing skin", "crimson red and ivory", 10007),
    ArchetypeSpec("Carmen", 25, "passionate intense gaze, delicate sculpted jawline", "thick lustrous dark curls pinned with tortoiseshell comb", "radiant sun-kissed olive complexion", "royal cobalt and gold", 20011),
    ArchetypeSpec("Sofia", 23, "captivating warm brown eyes, sweet heart-shaped face", "shoulder-length bouncy dark layered waves", "clear warm olive skin tone", "terracotta rust and sand", 30013),
    ArchetypeSpec("Elena", 25, "refined Andalusian beauty, prominent cheekbones", "sleek dark low chignon with face-framing tendrils", "golden-olive radiant skin", "emerald pine and champagne", 40017),
    ArchetypeSpec("Valeria", 24, "sharp model-like facial symmetry, deep dark gaze", "center-parted silky dark waves", "clear warm olive complexion", "deep wine and pearl", 50021),
    ArchetypeSpec("Martina", 23, "bright cheerful eyes, radiant dimpled smile", "modern textured dark lob with airy bounce", "sun-warmed olive skin", "mustard yellow and charcoal", 60029),
    ArchetypeSpec("Alba", 25, "poetic serene eyes, graceful defined chin", "luxurious thick dark braid with delicate clasp", "glowing honey-olive skin", "powder blue and cream", 70033),
    ArchetypeSpec("Claudia", 26, "commanding Mediterranean elegance, intense gaze", "voluminous side-swept glossy dark hair", "rich golden-olive skin tone", "sapphire blue and sand", 80039),
    ArchetypeSpec("Daniela", 24, "warm expressive almond eyes, captivating smile", "feathered layered dark waves", "clear olive-wheatish skin", "coral rose and navy", 90047),
    ArchetypeSpec("Paula", 25, "delicate refined features, sparkling dark eyes", "sleek straight raven hair with clean part", "radiant sun-kissed olive complexion", "burnt orange and ivory", 100051),
]

SPANISH_MALE_ARCHETYPES: list[ArchetypeSpec] = [
    ArchetypeSpec("Mateo", 26, "chiseled square jawline, intense deep dark eyes", "textured dark wavy hair swept back, neat stubble", "warm olive skin", "midnight navy and camel", 15017),
    ArchetypeSpec("Javier", 25, "sharp sculpted cheekbones, charismatic warm smile", "modern fade with textured dense top, clean-shaven", "sun-kissed golden-olive skin", "charcoal and burgundy", 25021),
    ArchetypeSpec("Alejandro", 27, "athletic broad-shouldered frame, intense gaze", "natural wavy dark locks, short trimmed box beard", "rich olive masculine complexion", "dark olive and oatmeal", 35027),
    ArchetypeSpec("Carlos", 26, "tall lean runner's build, sharp defined chin", "classic gentleman's side-part, light designer stubble", "clear warm olive skin tone", "espresso and champagne", 45031),
    ArchetypeSpec("Diego", 24, "youthful energetic charm, bright dark almond eyes", "modern textured quiff with clean edges, clean-shaven", "radiant golden-olive skin", "cobalt blue and grey", 55037),
    ArchetypeSpec("Lucas", 25, "slender athletic frame, piercing focused gaze", "tight taper fade, subtle shadow stubble", "sun-warmed olive skin", "forest green and black", 65041),
    ArchetypeSpec("Pablo", 26, "commanding Mediterranean poise, chiseled chin", "short military-style crop, neat short beard", "warm olive complexion", "maroon and cream", 75047),
    ArchetypeSpec("Alvaro", 25, "refined bone structure, captivating expressive eyes", "slicked-back textured dark hair, clean-shaven", "clear golden-olive skin", "slate blue and tan", 85053),
    ArchetypeSpec("Manuel", 27, "rugged masculine jawline, warm engaging smile", "textured crop with natural waves, trimmed stubble", "deep sun-kissed olive tone", "rust terracotta and navy", 95059),
    ArchetypeSpec("Daniel", 24, "athletic runner's physique, sharp angular jaw", "modern messy fringe haircut, light stubble", "golden-olive radiant skin", "chocolate and oatmeal", 105067),
]

# Korean Character Archetypes (ko) - Radiant glass skin, soft V-line jaw, bright expressive eyes, modern K-drama styling
KOREAN_FEMALE_ARCHETYPES: list[ArchetypeSpec] = [
    ArchetypeSpec("Ji-woo", 23, "delicate V-line jaw, bright expressive doe eyes", "glossy shoulder-length dark lob with see-through bangs", "radiant dewy glass porcelain skin", "pastel lilac and ivory", 10007),
    ArchetypeSpec("Min-seo", 24, "sweet heart-shaped face, charming dimpled smile", "long silky raven hair with soft airy waves", "clear porcelain-honey skin", "sky blue and cream", 20011),
    ArchetypeSpec("Ha-eun", 24, "refined cheekbones, captivating clear gaze", "modern textured wavy cut with subtle volume", "glowing glass skin tone", "coral peach and champagne", 30013),
    ArchetypeSpec("Su-jin", 25, "striking feline eyes, high sculpted cheekbones", "voluminous dark blowout waves", "luminous fair ivory skin", "cherry red and navy", 40017),
    ArchetypeSpec("Ye-eun", 23, "youthful radiance, bright almond eyes", "chic dark bob with tucked-back side", "dewy porcelain complexion", "sage green and pearl", 50021),
    ArchetypeSpec("Chae-won", 25, "poetic serene beauty, elegant slender jaw", "sleek low ponytail with clean middle part", "radiant warm ivory skin", "powder pink and charcoal", 60029),
    ArchetypeSpec("Da-eun", 24, "captivating warm gaze, delicate refined chin", "layered soft dark waves cascading over shoulders", "clear glass skin tone", "terracotta and cream", 70033),
    ArchetypeSpec("Seo-yeon", 26, "commanding K-drama elegance, sharp cheekbones", "side-parted glossy straight dark tresses", "porcelain-fair glowing complexion", "midnight cobalt and gold", 80039),
    ArchetypeSpec("Yu-jin", 24, "warm expressive eyes, cute subtle smile", "feathered modern layered dark hair", "sun-kissed warm ivory skin", "buttercup yellow and sand", 90047),
    ArchetypeSpec("Ji-min", 25, "graceful poise, large soulful dark brown eyes", "elegant half-updo with soft face tendrils", "radiant fair ivory skin", "royal plum and ivory", 100051),
]

KOREAN_MALE_ARCHETYPES: list[ArchetypeSpec] = [
    ArchetypeSpec("Min-jun", 25, "sharp chiseled jawline, captivating intense gaze", "modern two-block haircut with textured parting, clean-shaven", "clear radiant glass porcelain skin", "charcoal and ivory", 15017),
    ArchetypeSpec("Seo-jun", 26, "commanding K-drama lead presence, high cheekbones", "slicked-back textured dark hair, clean-shaven", "flawless fair-ivory complexion", "midnight navy and camel", 25021),
    ArchetypeSpec("Do-hyun", 24, "athletic lean frame, bright charismatic eyes", "textured comma hair styling, clean-shaven", "radiant warm ivory skin", "espresso and champagne", 35027),
    ArchetypeSpec("Jung-woo", 25, "slender fit build, sharp angular chin", "modern dandy cut with soft fringe, light shadow stubble", "clear porcelain skin tone", "forest green and black", 45031),
    ArchetypeSpec("Hyun-woo", 26, "broad-shouldered athletic build, warm smile", "classic gentleman's side-part, clean-shaven", "sun-warmed ivory complexion", "cobalt blue and grey", 55037),
    ArchetypeSpec("Si-woo", 24, "youthful energetic poise, sharp model jawline", "modern textured messy crop, clean-shaven", "glowing porcelain skin", "burgundy and oatmeal", 65041),
    ArchetypeSpec("Ji-ho", 25, "thoughtful deep gaze, refined facial symmetry", "naturally wavy layered dark locks, clean-shaven", "clear fair-ivory tone", "slate grey and sand", 75047),
    ArchetypeSpec("Seung-woo", 27, "commanding dignified presence, chiseled chin", "short tapered fade with dense top, neat stubble", "warm ivory skin tone", "dark olive and cream", 85053),
    ArchetypeSpec("Tae-hyung", 24, "captivating magnetic gaze, sculpted cheekbones", "voluminous wavy curtain haircut, clean-shaven", "radiant dewy skin", "royal blue and tan", 95059),
    ArchetypeSpec("Jin-woo", 26, "athletic runner's physique, sharp jawline", "short textured crew cut, clean-shaven", "clear porcelain-honey skin", "terracotta and charcoal", 105067),
]

# Western / Contemporary English Pop Archetypes (en) - Versatile contemporary Western features matching modern pop/indie aesthetic
WESTERN_FEMALE_ARCHETYPES: list[ArchetypeSpec] = [
    ArchetypeSpec("Emma", 24, "expressive almond hazel eyes, sculpted jawline", "shoulder-length golden-brunette blowout waves", "warm peach-fair radiant skin", "crimson red and ivory", 10007),
    ArchetypeSpec("Olivia", 23, "delicate heart-shaped face, bright blue eyes", "long natural wavy blonde tresses with face layers", "clear porcelain-fair skin", "sapphire blue and cream", 20011),
    ArchetypeSpec("Clara", 25, "defined cheekbones, warm brown eyes, gentle smile", "textured wavy dark chestnut bob", "sun-kissed warm golden skin", "emerald pine and sand", 30013),
    ArchetypeSpec("Maya", 24, "striking feline eyes, sharp sculpted chin", "voluminous dark brown curls cascading freely", "glowing warm caramel-honey skin", "terracotta rust and champagne", 40017),
    ArchetypeSpec("Ava", 23, "captivating doe eyes, cute dimpled cheeks", "modern curtain-fringed lob with soft bounce", "clear fair-ivory complexion", "powder blue and pearl", 50021),
    ArchetypeSpec("Harper", 25, "sharp model-like facial symmetry, green-grey gaze", "sleek straight dark hair with clean middle part", "radiant fair skin tone", "midnight navy and silver", 60029),
    ArchetypeSpec("Sophia", 24, "radiant smiling charm, deep warm brown eyes", "bouncy layered caramel waves", "sun-warmed honey skin", "burnt orange and ivory", 70033),
    ArchetypeSpec("Chloe", 25, "poetic serene eyes, graceful neckline", "loose romantic low bun with textured tendrils", "clear porcelain complexion", "royal plum and cream", 80039),
    ArchetypeSpec("Grace", 23, "delicate refined features, sparkling hazel eyes", "feathered shoulder-length wavy bob", "glowing peach-fair skin", "dusty rose and charcoal", 90047),
    ArchetypeSpec("Zoe", 26, "commanding modern poise, high sculpted cheekbones", "voluminous layered dark waves with soft luster", "warm golden-fair complexion", "mustard amber and slate", 100051),
]

WESTERN_MALE_ARCHETYPES: list[ArchetypeSpec] = [
    ArchetypeSpec("Liam", 26, "chiseled square jawline, intense blue-grey eyes", "textured modern crop with tapered sides, light stubble", "warm fair skin", "charcoal and camel", 15017),
    ArchetypeSpec("Ethan", 25, "sculpted angular cheekbones, warm hazel eyes", "classic comb-over with clean taper, clean-shaven", "clear fair-golden skin", "midnight navy and burgundy", 25021),
    ArchetypeSpec("Lucas", 26, "athletic lean runner's build, sharp defined chin", "naturally wavy brown hair pushed back, light stubble", "sun-warmed fair complexion", "dark olive and oatmeal", 35027),
    ArchetypeSpec("Noah", 24, "slender athletic frame, bright engaging brown eyes", "modern textured messy fringe, clean-shaven", "radiant fair skin tone", "espresso and champagne", 45031),
    ArchetypeSpec("Oliver", 25, "broad-shouldered fit frame, confident warm smile", "stylish pompadour with clean fade, light stubble", "clear porcelain-fair skin", "cobalt blue and grey", 55037),
    ArchetypeSpec("Caleb", 26, "strong masculine presence, deep-set dark eyes", "short military-style crop, neat trimmed beard", "warm golden-tan skin tone", "forest green and black", 65041),
    ArchetypeSpec("James", 25, "refined model bone structure, intense green eyes", "side-parted textured dark blonde hair, clean-shaven", "fair-ivory clear skin", "maroon and cream", 75047),
    ArchetypeSpec("Henry", 27, "commanding dignified posture, sharp cheekbones", "classic gentleman's taper, neat short beard", "sun-kissed fair complexion", "slate blue and tan", 85053),
    ArchetypeSpec("Jack", 24, "youthful energetic charm, bright hazel eyes", "feathered modern layered cut, light shadow stubble", "glowing fair skin", "rust terracotta and navy", 95059),
    ArchetypeSpec("Mason", 26, "chiseled jawline, warm charismatic gaze", "natural wavy dark brown locks, clean-shaven", "clear warm fair tone", "chocolate and ivory", 105067),
]

__all__ = [
    "JAPANESE_FEMALE_ARCHETYPES", "JAPANESE_MALE_ARCHETYPES",
    "FRENCH_FEMALE_ARCHETYPES", "FRENCH_MALE_ARCHETYPES",
    "SPANISH_FEMALE_ARCHETYPES", "SPANISH_MALE_ARCHETYPES",
    "KOREAN_FEMALE_ARCHETYPES", "KOREAN_MALE_ARCHETYPES",
    "WESTERN_FEMALE_ARCHETYPES", "WESTERN_MALE_ARCHETYPES",
]
