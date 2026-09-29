from app.services.extraction_service import extract_requirements
def test_led_extraction():
    r=extract_requirements("We need outdoor LED street lights with 90W, IP66 and minimum 90 lm/W.")
    assert r["product"]=="LED street light"
    assert r["entities"]["ip"]=="IP66"
    assert r["entities"]["efficacy"]=="90"
