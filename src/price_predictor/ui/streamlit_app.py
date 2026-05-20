"""Streamlit demo front-end.

Renders a form, POSTs the request to the FastAPI service running on
``http://127.0.0.1:8000`` inside the same container (supervisord wires
both processes, see ADR 0004), and displays the price + conformal
interval. All UI code lives in :func:`main` so importing the module has
no side effects (keeps it unit-testable); ``streamlit run`` executes
this file as ``__main__`` and the guard at the bottom invokes ``main``.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any

import streamlit as st

from price_predictor import __version__

API_URL = os.environ.get("PP_INTERNAL_API_URL", "http://127.0.0.1:8000")
_TIMEOUT = 30

# Approximate city centre coordinates so the user can pick a city and
# get a sensible lat/lon default without consulting a map.
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
        f"v{__version__} · Polish apartment price estimates with conformal "
        "intervals · model pulled from MLflow registry at startup"
    )

    with st.form("predict"):
        col1, col2 = st.columns(2)
        with col1:
            city = st.selectbox("City", sorted(_CITY_CENTRES), index=14)
            lat_default, lon_default = _CITY_CENTRES[city]
            square_meters = st.number_input("Area (m²)", 25.0, 150.0, 55.0, step=1.0)
            rooms = st.number_input("Rooms", 1, 10, 3, step=1)
            floor = st.number_input("Floor", 0, 30, 2, step=1)
            floor_count = st.number_input("Total floors", 1, 30, 5, step=1)
            build_year = st.number_input("Build year", 1850, 2024, 2010, step=1)
        with col2:
            latitude = st.number_input("Latitude", 49.0, 55.0, lat_default, step=0.01)
            longitude = st.number_input("Longitude", 14.0, 24.0, lon_default, step=0.01)
            centre_distance_km = st.number_input(
                "Distance to centre (km)", 0.0, 30.0, 3.0, step=0.1
            )
            poi_count = st.number_input("POI count nearby", 0, 200, 20, step=1)
            property_type = st.selectbox(
                "Type", ["", "apartmentBuilding", "blockOfFlats", "tenement"]
            )
            ownership = st.selectbox("Ownership", ["condominium", "cooperative", "udział"])

        st.markdown("**Amenities**")
        a1, a2, a3, a4, a5 = st.columns(5)
        with a1:
            has_parking = st.checkbox("Parking", value=False)
        with a2:
            has_balcony = st.checkbox("Balcony", value=True)
        with a3:
            has_elevator = st.checkbox("Elevator", value=False)
        with a4:
            has_security = st.checkbox("Security", value=False)
        with a5:
            has_storage = st.checkbox("Storage", value=False)

        submitted = st.form_submit_button("Predict price", type="primary")

    if not submitted:
        st.info(
            "Fill the form and click **Predict price**. The trained model "
            "is fetched from the registry at container startup; cold "
            "requests are fast (≈ 50 ms)."
        )
        return

    payload: dict[str, Any] = {
        "city": city,
        "square_meters": float(square_meters),
        "rooms": int(rooms),
        "floor": int(floor),
        "floor_count": int(floor_count),
        "build_year": int(build_year),
        "latitude": float(latitude),
        "longitude": float(longitude),
        "centre_distance_km": float(centre_distance_km),
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
        st.error(f"API returned HTTP {exc.code}: {detail}")
        return
    except urllib.error.URLError as exc:
        st.error(f"Could not reach the API: {exc.reason}")
        return

    price = result["predicted_price"]
    lo = result.get("interval_low")
    hi = result.get("interval_high")
    st.success(f"Estimated price: **{_fmt_pln(price)}**")
    if lo is not None and hi is not None:
        st.metric(
            label="90% conformal interval",
            value=f"{_fmt_pln(lo)} — {_fmt_pln(hi)}",
            delta=f"± {_fmt_pln((hi - lo) / 2)}",
        )
    st.caption(
        f"Model: `{result['model_name']}` v{result['model_version']} · "
        f"served at {result['predicted_at']}"
    )
    with st.expander("Raw response"):
        st.json(result)


if __name__ == "__main__":
    main()
