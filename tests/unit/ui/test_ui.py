"""Importing the UI module must have no Streamlit side effects."""

from __future__ import annotations

from price_predictor.ui import main


def test_main_is_callable() -> None:
    assert callable(main)
