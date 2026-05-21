"""Importing the UI module must have no Streamlit side effects."""

from __future__ import annotations

import pytest

from price_predictor.ui import main
from price_predictor.ui.streamlit_app import (
    _CITY_CENTRES,
    _DISTRICT_CENTRE,
    _DISTRICT_OTHER,
    _model_badge,
    _resolve_from_choice,
    _resolve_location,
)


def test_main_is_callable() -> None:
    assert callable(main)


def test_resolve_location_matches_known_district() -> None:
    location = _resolve_location("warszawa", "Mokotów, okolice metra")

    assert location.matched is True
    assert location.label == "Mokotów"
    assert (location.latitude, location.longitude) != _CITY_CENTRES["warszawa"]
    assert location.centre_distance_km > 0


def test_resolve_location_matches_accents_inside_address() -> None:
    location = _resolve_location("lodz", "ul. Piotrkowska 100, Śródmieście")

    assert location.matched is True
    assert location.label == "Śródmieście"


def test_resolve_location_falls_back_to_city_centre_for_unknown_text() -> None:
    location = _resolve_location("gdansk", "nieznane osiedle testowe")

    assert location.matched is False
    assert location.label == "Gdańsk centrum"
    assert (location.latitude, location.longitude) == _CITY_CENTRES["gdansk"]
    assert location.centre_distance_km == 0.0


def test_resolve_from_choice_centre_sentinel_uses_city_centre() -> None:
    location = _resolve_from_choice("warszawa", _DISTRICT_CENTRE, "")

    assert location.matched is True
    assert (location.latitude, location.longitude) == _CITY_CENTRES["warszawa"]
    assert location.centre_distance_km == 0.0
    assert "centrum" in location.label.lower()


def test_resolve_from_choice_named_district_picks_district_coords() -> None:
    location = _resolve_from_choice("warszawa", "Ursynów", "")

    assert location.matched is True
    assert location.label == "Ursynów"
    assert (location.latitude, location.longitude) != _CITY_CENTRES["warszawa"]
    assert location.centre_distance_km > 0


def test_resolve_from_choice_other_with_hint_falls_back_to_fuzzy_match() -> None:
    location = _resolve_from_choice("krakow", _DISTRICT_OTHER, "Kazimierz, blisko Wisły")

    assert location.matched is True
    assert location.label == "Kazimierz"


def test_resolve_from_choice_other_with_unknown_hint_flags_unmatched() -> None:
    location = _resolve_from_choice("krakow", _DISTRICT_OTHER, "zupełnie nieznany adres")

    assert location.matched is False
    assert (location.latitude, location.longitude) == _CITY_CENTRES["krakow"]


def test_resolve_from_choice_unknown_district_raises() -> None:
    # Programmer error — the UI builds the dropdown from _DISTRICTS, so a
    # label not present in the city's list should surface loudly, not
    # silently degrade to the city centre.
    with pytest.raises(ValueError, match="unknown district"):
        _resolve_from_choice("warszawa", "Atlantyda", "")


def test_resolve_from_choice_other_without_hint_uses_centre_silently() -> None:
    location = _resolve_from_choice("gdansk", _DISTRICT_OTHER, "")

    # No hint => no warning => matched stays True (= "user accepts centre").
    assert location.matched is True
    assert (location.latitude, location.longitude) == _CITY_CENTRES["gdansk"]


def test_model_badge_none_when_health_missing() -> None:
    assert _model_badge(None) is None
    assert _model_badge({"status": "ok"}) is None
    assert _model_badge({"status": "ok", "model_info": None}) is None


def test_model_badge_renders_loaded_state() -> None:
    badge = _model_badge(
        {
            "status": "ok",
            "model_info": {
                "name": "price-predictor",
                "version": "1",
                "stage": "production",
                "loaded": True,
            },
        }
    )
    assert badge is not None
    assert "price-predictor" in badge
    assert "v1" in badge
    assert "production" in badge
    assert "załadowany" in badge


def test_model_badge_renders_unloaded_state() -> None:
    badge = _model_badge(
        {
            "status": "ok",
            "model_info": {
                "name": "price-predictor",
                "version": "unknown",
                "stage": "production",
                "loaded": False,
            },
        }
    )
    assert badge is not None
    assert "nie załadowany" in badge
