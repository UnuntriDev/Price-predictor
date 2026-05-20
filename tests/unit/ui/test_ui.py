"""Importing the UI module must have no Streamlit side effects."""

from __future__ import annotations

from price_predictor.ui import main
from price_predictor.ui.streamlit_app import _CITY_CENTRES, _resolve_location


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
