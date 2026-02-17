import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path

st.set_page_config(
    page_title="SAR AI Platform",
    page_icon="📋",
    layout="wide"
)

# REMOVE default padding + margins
st.markdown("""
<style>
.block-container {
    padding: 0rem !important;
    margin: 0rem !important;
    max-width: 100% !important;
}

iframe {
    width: 100vw !important;
    height: 100vh !important;
    border: none !important;
}

header, footer {visibility:hidden;}
</style>
""", unsafe_allow_html=True)

html_path = Path(__file__).parent / "frontend_ui.html"

if html_path.exists():
    html_code = html_path.read_text(encoding="utf-8")
    components.html(html_code, height=1200, scrolling=True)
else:
    st.error("HTML UI file not found")
