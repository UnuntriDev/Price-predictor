"""Streamlit demo front-end.

Renders a form, POSTs the request to the FastAPI service running on
``http://127.0.0.1:8000`` inside the same container (supervisord wires
both processes, see ADR 0004), and displays the price + conformal
interval. All UI code lives in :func:`main` so importing the module has
no side effects (keeps it unit-testable); ``streamlit run`` executes
this file as ``__main__`` and the guard at the bottom invokes ``main``.

Labels are in Polish (the model is Polish-market-only); API values
stay lowercase ASCII to satisfy the CityEnum / OwnershipType contracts.
The user supplies a city plus an address/district. The UI resolves a
known district locally to approximate coordinates and falls back to the
city centre when the text cannot be matched.
"""

from __future__ import annotations

import json
import math
import os
import re
import unicodedata
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any

import streamlit as st

API_URL = os.environ.get("PP_INTERNAL_API_URL", "http://127.0.0.1:8000")
_TIMEOUT = 30

# Display name (Polish, proper case) -> approximate city-centre coords.
# The dict key is the canonical API value (lowercase ASCII, CityEnum).
_CITY_CENTRES: dict[str, tuple[float, float]] = {
    "warszawa": (52.2297, 21.0122),
    "krakow": (50.0647, 19.9450),
    "wroclaw": (51.1079, 17.0385),
    "poznan": (52.4064, 16.9252),
    "gdansk": (54.3520, 18.6466),
    "gdynia": (54.5189, 18.5305),
    "szczecin": (53.4285, 14.5528),
    "bydgoszcz": (53.1235, 18.0084),
    "lublin": (51.2465, 22.5684),
    "katowice": (50.2649, 19.0238),
    "bialystok": (53.1325, 23.1688),
    "lodz": (51.7592, 19.4560),
    "czestochowa": (50.8118, 19.1203),
    "radom": (51.4027, 21.1471),
    "rzeszow": (50.0413, 21.9990),
}
_CITY_PL: dict[str, str] = {
    "warszawa": "Warszawa",
    "krakow": "Kraków",
    "wroclaw": "Wrocław",
    "poznan": "Poznań",
    "gdansk": "Gdańsk",
    "gdynia": "Gdynia",
    "szczecin": "Szczecin",
    "bydgoszcz": "Bydgoszcz",
    "lublin": "Lublin",
    "katowice": "Katowice",
    "bialystok": "Białystok",
    "lodz": "Łódź",
    "czestochowa": "Częstochowa",
    "radom": "Radom",
    "rzeszow": "Rzeszów",
}
_PROPERTY_TYPE_PL: dict[str, str] = {
    "": "— (nie podano)",
    "apartmentBuilding": "Apartamentowiec",
    "blockOfFlats": "Blok",
    "tenement": "Kamienica",
}
_OWNERSHIP_PL: dict[str, str] = {
    "condominium": "Własność",
    "cooperative": "Spółdzielcze własnościowe",
    "udział": "Udział",
}


@dataclass(frozen=True)
class LocationResolution:
    """Approximate location used to build the API payload."""

    latitude: float
    longitude: float
    centre_distance_km: float
    label: str
    matched: bool


@dataclass(frozen=True)
class _KnownPlace:
    label: str
    latitude: float
    longitude: float


_DISTRICTS: dict[str, tuple[_KnownPlace, ...]] = {
    "warszawa": (
        _KnownPlace("Śródmieście", 52.2320, 21.0190),
        _KnownPlace("Mokotów", 52.1930, 21.0340),
        _KnownPlace("Wola", 52.2390, 20.9600),
        _KnownPlace("Praga-Południe", 52.2450, 21.0830),
        _KnownPlace("Ursynów", 52.1410, 21.0490),
        _KnownPlace("Bielany", 52.2870, 20.9490),
        _KnownPlace("Wilanów", 52.1650, 21.0900),
    ),
    "krakow": (
        _KnownPlace("Stare Miasto", 50.0610, 19.9360),
        _KnownPlace("Kazimierz", 50.0510, 19.9440),
        _KnownPlace("Podgórze", 50.0390, 19.9570),
        _KnownPlace("Krowodrza", 50.0800, 19.9180),
        _KnownPlace("Nowa Huta", 50.0720, 20.0370),
    ),
    "wroclaw": (
        _KnownPlace("Stare Miasto", 51.1100, 17.0320),
        _KnownPlace("Krzyki", 51.0740, 17.0290),
        _KnownPlace("Fabryczna", 51.1200, 16.9700),
        _KnownPlace("Psie Pole", 51.1430, 17.1100),
        _KnownPlace("Śródmieście", 51.1180, 17.0610),
    ),
    "poznan": (
        _KnownPlace("Stare Miasto", 52.4080, 16.9340),
        _KnownPlace("Jeżyce", 52.4140, 16.8950),
        _KnownPlace("Grunwald", 52.3900, 16.8800),
        _KnownPlace("Wilda", 52.3900, 16.9200),
        _KnownPlace("Nowe Miasto", 52.3970, 16.9900),
    ),
    "gdansk": (
        _KnownPlace("Śródmieście", 54.3480, 18.6540),
        _KnownPlace("Wrzeszcz", 54.3800, 18.6000),
        _KnownPlace("Oliwa", 54.4100, 18.5600),
        _KnownPlace("Przymorze", 54.4140, 18.5900),
        _KnownPlace("Morena", 54.3600, 18.5800),
    ),
    "gdynia": (
        _KnownPlace("Śródmieście", 54.5190, 18.5400),
        _KnownPlace("Orłowo", 54.4750, 18.5540),
        _KnownPlace("Redłowo", 54.4920, 18.5440),
        _KnownPlace("Chylonia", 54.5480, 18.4620),
        _KnownPlace("Dąbrowa", 54.4720, 18.4700),
    ),
    "szczecin": (
        _KnownPlace("Śródmieście", 53.4280, 14.5530),
        _KnownPlace("Pogodno", 53.4400, 14.5000),
        _KnownPlace("Gumieńce", 53.4050, 14.4850),
        _KnownPlace("Niebuszewo", 53.4550, 14.5500),
        _KnownPlace("Warszewo", 53.4780, 14.5450),
    ),
    "bydgoszcz": (
        _KnownPlace("Śródmieście", 53.1230, 18.0080),
        _KnownPlace("Fordon", 53.1500, 18.1700),
        _KnownPlace("Bartodzieje", 53.1300, 18.0450),
        _KnownPlace("Wyżyny", 53.1030, 18.0300),
        _KnownPlace("Szwederowo", 53.1110, 17.9900),
    ),
    "lublin": (
        _KnownPlace("Śródmieście", 51.2470, 22.5680),
        _KnownPlace("Czechów", 51.2750, 22.5400),
        _KnownPlace("Wieniawa", 51.2520, 22.5350),
        _KnownPlace("Czuby", 51.2300, 22.5100),
        _KnownPlace("Bronowice", 51.2390, 22.5900),
    ),
    "katowice": (
        _KnownPlace("Śródmieście", 50.2600, 19.0200),
        _KnownPlace("Ligota", 50.2200, 18.9700),
        _KnownPlace("Koszutka", 50.2740, 19.0200),
        _KnownPlace("Brynów", 50.2350, 19.0150),
        _KnownPlace("Dąb", 50.2720, 18.9900),
    ),
    "bialystok": (
        _KnownPlace("Centrum", 53.1320, 23.1680),
        _KnownPlace("Bojary", 53.1360, 23.1760),
        _KnownPlace("Antoniuk", 53.1450, 23.1350),
        _KnownPlace("Piasta", 53.1260, 23.1900),
        _KnownPlace("Wysoki Stoczek", 53.1500, 23.1250),
    ),
    "lodz": (
        _KnownPlace("Śródmieście", 51.7680, 19.4560),
        _KnownPlace("Bałuty", 51.8000, 19.4550),
        _KnownPlace("Polesie", 51.7600, 19.4100),
        _KnownPlace("Widzew", 51.7600, 19.5300),
        _KnownPlace("Górna", 51.7300, 19.4700),
    ),
    "czestochowa": (
        _KnownPlace("Śródmieście", 50.8110, 19.1200),
        _KnownPlace("Tysiąclecie", 50.8270, 19.1250),
        _KnownPlace("Raków", 50.7850, 19.1650),
        _KnownPlace("Północ", 50.8350, 19.1000),
        _KnownPlace("Wrzosowiak", 50.7900, 19.1350),
    ),
    "radom": (
        _KnownPlace("Śródmieście", 51.4020, 21.1470),
        _KnownPlace("Ustronie", 51.3900, 21.1650),
        _KnownPlace("Gołębiów", 51.4300, 21.1550),
        _KnownPlace("Michałów", 51.4250, 21.1200),
        _KnownPlace("Zamłynie", 51.4050, 21.1200),
    ),
    "rzeszow": (
        _KnownPlace("Śródmieście", 50.0410, 21.9990),
        _KnownPlace("Baranówka", 50.0600, 21.9850),
        _KnownPlace("Nowe Miasto", 50.0250, 22.0150),
        _KnownPlace("Drabinianka", 50.0150, 21.9950),
        _KnownPlace("Pobitno", 50.0400, 22.0300),
    ),
}

_POLISH_TRANSLATION = str.maketrans({"ł": "l", "Ł": "l"})


def _normalise_location(text: str) -> str:
    asciiish = unicodedata.normalize("NFKD", text.casefold().translate(_POLISH_TRANSLATION))
    no_accents = "".join(ch for ch in asciiish if not unicodedata.combining(ch))
    return re.sub(r"[^a-z0-9]+", " ", no_accents).strip()


def _haversine_km(start: tuple[float, float], end: tuple[float, float]) -> float:
    lat1, lon1 = (math.radians(value) for value in start)
    lat2, lon2 = (math.radians(value) for value in end)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 6_371.0 * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def _resolve_location(city: str, address_or_district: str) -> LocationResolution:
    centre = _CITY_CENTRES[city]
    query = _normalise_location(address_or_district)
    if query:
        for place in _DISTRICTS.get(city, ()):
            if re.search(rf"\b{re.escape(_normalise_location(place.label))}\b", query):
                point = (place.latitude, place.longitude)
                return LocationResolution(
                    latitude=place.latitude,
                    longitude=place.longitude,
                    centre_distance_km=round(_haversine_km(centre, point), 2),
                    label=place.label,
                    matched=True,
                )

    return LocationResolution(
        latitude=centre[0],
        longitude=centre[1],
        centre_distance_km=0.0,
        label=f"{_CITY_PL[city]} centrum",
        matched=not query,
    )


def _call_predict(payload: dict[str, Any]) -> dict[str, Any]:
    req = urllib.request.Request(
        f"{API_URL}/predict",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
        body: dict[str, Any] = json.loads(resp.read().decode("utf-8"))
        return body


def _fmt_pln(value: int | float) -> str:
    return f"{round(value):,} PLN".replace(",", " ")


def main() -> None:
    """Render the valuation page."""
    st.set_page_config(page_title="PricePredictor", layout="centered")
    st.title("PricePredictor")
    st.caption(
        "Wycena polskich mieszkań z przedziałami conformal · "
        "model pobierany z rejestru MLflow przy starcie kontenera"
    )

    with st.form("predict"):
        col1, col2 = st.columns(2)
        with col1:
            city = st.selectbox(
                "Miasto",
                list(_CITY_PL),
                index=0,
                format_func=lambda v: _CITY_PL[v],
            )
            address_or_district = st.text_input(
                "Adres lub dzielnica",
                placeholder="np. Mokotów, Stare Miasto, ul. Długa",
            )
            square_meters = st.number_input("Powierzchnia (m²)", 25.0, 150.0, 55.0, step=1.0)
            rooms = st.number_input("Liczba pokoi", 1, 10, 3, step=1)
            floor = st.number_input("Piętro", 0, 30, 2, step=1)
        with col2:
            floor_count = st.number_input("Liczba pięter w budynku", 1, 30, 5, step=1)
            build_year = st.number_input("Rok budowy", 1850, 2024, 2010, step=1)
            poi_count = st.number_input("Liczba punktów POI w pobliżu", 0, 200, 20, step=1)
            property_type = st.selectbox(
                "Typ budynku",
                list(_PROPERTY_TYPE_PL),
                format_func=lambda v: _PROPERTY_TYPE_PL[v],
            )
            ownership = st.selectbox(
                "Forma własności",
                list(_OWNERSHIP_PL),
                format_func=lambda v: _OWNERSHIP_PL[v],
            )

        st.markdown("**Udogodnienia**")
        a1, a2, a3, a4, a5 = st.columns(5)
        with a1:
            has_parking = st.checkbox("Parking", value=False)
        with a2:
            has_balcony = st.checkbox("Balkon", value=True)
        with a3:
            has_elevator = st.checkbox("Winda", value=False)
        with a4:
            has_security = st.checkbox("Ochrona", value=False)
        with a5:
            has_storage = st.checkbox("Komórka", value=False)

        submitted = st.form_submit_button("Oszacuj cenę", type="primary")

    if not submitted:
        st.info(
            "Wypełnij formularz i kliknij **Oszacuj cenę**. Model jest "
            "pobierany z rejestru MLflow przy starcie kontenera; każde "
            "kolejne zapytanie odpowiada w ≈ 50 ms."
        )
        return

    location = _resolve_location(city, address_or_district)
    payload: dict[str, Any] = {
        "city": city,
        "square_meters": float(square_meters),
        "rooms": int(rooms),
        "floor": int(floor),
        "floor_count": int(floor_count),
        "build_year": int(build_year),
        "latitude": location.latitude,
        "longitude": location.longitude,
        "centre_distance_km": location.centre_distance_km,
        "poi_count": int(poi_count),
        "ownership": ownership,
        "has_parking": bool(has_parking),
        "has_balcony": bool(has_balcony),
        "has_elevator": bool(has_elevator),
        "has_security": bool(has_security),
        "has_storage": bool(has_storage),
    }
    if property_type:
        payload["property_type"] = property_type

    try:
        result = _call_predict(payload)
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        st.error(f"API zwróciło HTTP {exc.code}: {detail}")
        return
    except urllib.error.URLError as exc:
        st.error(f"Nie udało się połączyć z API: {exc.reason}")
        return

    price = result["predicted_price"]
    lo = result.get("interval_low")
    hi = result.get("interval_high")
    if address_or_district and not location.matched:
        st.warning(
            "Nie rozpoznano dzielnicy lub adresu lokalnie, więc użyto centrum miasta. "
            "Model nie wysyła adresu do zewnętrznego geokodera."
        )
    st.success(f"Szacowana cena: **{_fmt_pln(price)}**")
    if lo is not None and hi is not None:
        st.metric(
            label="Przedział ufności conformal (90%)",
            value=f"{_fmt_pln(lo)} — {_fmt_pln(hi)}",
            delta=f"± {_fmt_pln((hi - lo) / 2)}",
        )
    st.caption(
        f"Model: `{result['model_name']}` v{result['model_version']} · "
        f"lokalizacja: {location.label}, {location.centre_distance_km:.1f} km od centrum · "
        f"zwrócono o {result['predicted_at']}"
    )
    with st.expander("Surowa odpowiedź API"):
        st.json(result)


if __name__ == "__main__":
    main()
