"""Streamlit demo front-end (skeleton).

UI code is wrapped in :func:`main` so importing the module has no side
effects (keeps it unit-testable); ``streamlit run`` executes this file
as ``__main__`` and the guard at the bottom invokes :func:`main`.
"""

from __future__ import annotations

import streamlit as st

from price_predictor import __version__


def main() -> None:
    """Render the valuation page."""
    st.set_page_config(page_title="PricePredictor", layout="centered")
    st.title("PricePredictor")
    st.caption(f"v{__version__} - Polish real-estate price estimates")
    st.info(
        "Phase 1 skeleton: the prediction form and API call are wired in "
        "Phase 2. This page exists so the deployment target is real."
    )


if __name__ == "__main__":
    main()
