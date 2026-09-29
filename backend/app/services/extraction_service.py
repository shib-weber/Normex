import re

DOMAIN_WORDS = {
    "Lighting": ["led", "luminaire", "street light", "streetlight", "lighting", "lamp", "lumen", "lm/w"],
    "Electrical": ["cable", "transformer", "voltage", "current", "electrical", "harmonic", "emc", "earthing", "ip66", "ip65"],
    "Solar": ["solar", "photovoltaic", "pv", "module", "inverter"],
    "Construction": ["cement", "steel", "concrete", "construction", "structural"],
    "Medical": ["hospital", "medical", "ppe", "glove", "mask"],
    "Water": ["water", "pump", "pipeline", "treatment"],
    "Transport": ["ev charging", "electric vehicle", "charger", "transport"],
    "IT": ["data centre", "data center", "server", "switch", "router", "network"],
}


def detect_language(text: str) -> str:
    if re.search(r"[\u0900-\u097F]", text):
        return "hi"
    if re.search(r"[\u0980-\u09FF]", text):
        return "bn"
    return "en"


def _find(pattern, text, flags=re.I):
    m = re.search(pattern, text, flags)
    return m.group(1) if m else None


def _findall(pattern, text, flags=re.I):
    return re.findall(pattern, text, flags)


def extract_requirements(text: str) -> dict:
    text = text or ""
    lower = text.lower()
    product = None
    if "street light" in lower or "streetlight" in lower or "road lighting" in lower:
        product = "LED road/street lighting luminaire"
    elif "solar pv" in lower or "photovoltaic" in lower:
        product = "Solar PV system"
    elif "cable" in lower:
        product = "Electrical cable"

    domain = next((d for d, words in DOMAIN_WORDS.items() if any(w in lower for w in words)), "General")
    power = _find(r"(?:approximately|approx\.?|about|of|rated at|rated)\s*(\d+(?:\.\d+)?)\s*(?:w|watt|watts)\b", text)
    if not power:
        power = _find(r"\b(\d+(?:\.\d+)?)\s*(?:w|watt|watts)\b", text)
    efficacy = _find(r"(?:minimum|min\.?|at least|>=|not less than)\s*(\d+(?:\.\d+)?)\s*lm\s*/\s*w", text)
    ip = _find(r"\b(IP\s*\d{2})\b", text)
    voltage = _find(r"\b(\d+(?:\.\d+)?)\s*(?:v|volt|volts)\b", text)
    quantity = _find(r"\b(?:quantity|qty)\s*[:=-]?\s*(\d[\d,]*)\b", text)
    standards = _findall(r"\bIS\s*(?:/IEC\s*)?\d{2,6}(?:\s*\([^\n,;]{1,80}\))?(?:\s*:\s*\d{4})?", text)

    requirements = []
    if product:
        requirements.append({"name": "Product type", "value": product, "operator": "=", "covered": True})
    if quantity:
        requirements.append({"name": "Quantity", "value": int(quantity.replace(",", "")), "operator": "=", "covered": True})
    if power:
        requirements.append({"name": "Power", "value": float(power), "unit": "W", "operator": "=", "covered": True})
    if efficacy:
        requirements.append({"name": "Luminous efficacy", "value": float(efficacy), "unit": "lm/W", "operator": ">=", "covered": True})
    if ip:
        requirements.append({"name": "Ingress protection", "value": re.sub(r"\s+", "", ip).upper(), "operator": "=", "covered": True})
    if voltage:
        requirements.append({"name": "Supply voltage", "value": float(voltage), "unit": "V", "operator": "=", "covered": True})
    if "surge" in lower:
        requirements.append({"name": "Surge protection", "value": "Required", "operator": "=", "covered": True})
    if "installation" not in lower and "install" not in lower:
        requirements.append({"name": "Installation requirements", "value": None, "operator": "missing", "covered": False})
    if "acceptance" not in lower and "commissioning" not in lower:
        requirements.append({"name": "Acceptance criteria", "value": None, "operator": "missing", "covered": False})
    if "test" not in lower and "testing" not in lower:
        requirements.append({"name": "Test method", "value": None, "operator": "missing", "covered": False})
    if "warranty" not in lower:
        requirements.append({"name": "Warranty", "value": None, "operator": "missing", "covered": False})

    return {
        "original_input": text,
        "language": detect_language(text),
        "product": product or "Unspecified procurement product",
        "domain": domain,
        "requirements": requirements,
        "existing_standards": standards,
        "entities": {"power": power, "efficacy": efficacy, "ip": ip, "voltage": voltage, "quantity": quantity},
    }
