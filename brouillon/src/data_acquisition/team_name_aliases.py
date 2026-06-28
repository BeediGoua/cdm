import re
import unicodedata


def normalize_text(value: str) -> str:
    if not value:
        return ""
    normalized = unicodedata.normalize("NFKD", value)
    normalized = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    normalized = normalized.lower().strip()
    normalized = re.sub(r"[^a-z0-9]+", " ", normalized)
    return normalized.strip()


TEAM_NAME_ALIASES = {

    # =========================
    # AFRICA
    # =========================

    "algeria": "algeria",
    "algérie": "algeria",

    "angola": "angola",

    "benin": "benin",

    "botswana": "botswana",

    "burkina faso": "burkina faso",

    "cameroon": "cameroon",
    "cameroun": "cameroon",

    "cape verde": "cabo verde",
    "cabo verde": "cabo verde",

    "central african republic": "central african republic",

    "chad": "chad",

    "comoros": "comoros",

    "congo": "congo",
    "republic of congo": "congo",

    "dr congo": "congo dr",
    "d r congo": "congo dr",
    "democratic republic of congo": "congo dr",
    "congo dr": "congo dr",
    "rd congo": "congo dr",

    "cote d ivoire": "cote d ivoire",
    "cote d'ivoire": "cote d ivoire",
    "côte d'ivoire": "cote d ivoire",
    "ivory coast": "cote d ivoire",

    "egypt": "egypt",
    "egypte": "egypt",

    "equatorial guinea": "equatorial guinea",

    "ethiopia": "ethiopia",

    "gabon": "gabon",

    "gambia": "gambia",

    "ghana": "ghana",

    "guinea": "guinea",

    "guinea-bissau": "guinea-bissau",
    "guinea bissau": "guinea-bissau",

    "kenya": "kenya",

    "libya": "libya",

    "madagascar": "madagascar",

    "mali": "mali",

    "mauritania": "mauritania",

    "morocco": "morocco",
    "maroc": "morocco",

    "mozambique": "mozambique",

    "namibia": "namibia",

    "nigeria": "nigeria",

    "senegal": "senegal",

    "south africa": "south africa",
    "rsa": "south africa",

    "sudan": "sudan",

    "tanzania": "tanzania",

    "tunisia": "tunisia",
    "tunisie": "tunisia",

    "uganda": "uganda",

    "zambia": "zambia",

    "zimbabwe": "zimbabwe",

    # =========================
    # ASIA
    # =========================

    "australia": "australia",

    "bahrain": "bahrain",

    "china": "china pr",
    "china pr": "china pr",
    "pr china": "china pr",

    "india": "india",

    "indonesia": "indonesia",

    "iran": "ir iran",
    "ir iran": "ir iran",

    "iraq": "iraq",

    "japan": "japan",

    "jordan": "jordan",

    "kuwait": "kuwait",

    "north korea": "north korea",
    "dpr korea": "north korea",

    "south korea": "korea republic",
    "korea republic": "korea republic",
    "republic of korea": "korea republic",

    "oman": "oman",

    "palestine": "palestine",

    "qatar": "qatar",

    "saudi arabia": "saudi arabia",

    "syria": "syria",

    "tajikistan": "tajikistan",

    "thailand": "thailand",

    "uae": "united arab emirates",
    "united arab emirates": "united arab emirates",

    "uzbekistan": "uzbekistan",

    "vietnam": "vietnam",

    # =========================
    # EUROPE
    # =========================

    "albania": "albania",
    "austria": "austria",
    "belgium": "belgium",
    "bosnia herzegovina": "bosnia and herzegovina",
    "bosnia and herzegovina": "bosnia and herzegovina",
    "bulgaria": "bulgaria",
    "croatia": "croatia",
    "czech republic": "czechia",
    "czechia": "czechia",
    "denmark": "denmark",
    "england": "england",
    "finland": "finland",
    "france": "france",
    "georgia": "georgia",
    "germany": "germany",
    "greece": "greece",
    "hungary": "hungary",
    "iceland": "iceland",
    "ireland": "ireland",
    "republic of ireland": "ireland",
    "israel": "israel",
    "italy": "italy",
    "montenegro": "montenegro",
    "netherlands": "netherlands",
    "holland": "netherlands",
    "north macedonia": "north macedonia",
    "norway": "norway",
    "poland": "poland",
    "portugal": "portugal",
    "romania": "romania",
    "scotland": "scotland",
    "serbia": "serbia",
    "slovakia": "slovakia",
    "slovenia": "slovenia",
    "spain": "spain",
    "sweden": "sweden",
    "switzerland": "switzerland",
    "turkey": "turkiye",
    "türkiye": "turkiye",
    "turkiye": "turkiye",
    "ukraine": "ukraine",
    "wales": "wales",

    # =========================
    # NORTH / CENTRAL AMERICA
    # =========================

    "canada": "canada",

    "costa rica": "costa rica",

    "curacao": "curaçao",
    "curaçao": "curaçao",

    "el salvador": "el salvador",

    "guatemala": "guatemala",

    "haiti": "haiti",

    "honduras": "honduras",

    "jamaica": "jamaica",

    "mexico": "mexico",

    "panama": "panama",

    "united states": "usa",
    "united states of america": "usa",
    "usa": "usa",
    "u s a": "usa",
    "u.s.a.": "usa",
    "us": "usa",

    # =========================
    # SOUTH AMERICA
    # =========================

    "argentina": "argentina",
    "bolivia": "bolivia",
    "brazil": "brazil",
    "brasil": "brazil",
    "chile": "chile",
    "colombia": "colombia",
    "ecuador": "ecuador",
    "paraguay": "paraguay",
    "peru": "peru",
    "uruguay": "uruguay",
    "venezuela": "venezuela",

    # =========================
    # OCEANIA
    # =========================

    "new zealand": "new zealand",
    "nz": "new zealand",

    "fiji": "fiji",

    "new caledonia": "new caledonia",

}

# Normalize alias keys and values so lookup works after accent stripping.
TEAM_NAME_ALIASES = {
    normalize_text(key): normalize_text(value)
    for key, value in TEAM_NAME_ALIASES.items()
}

