import streamlit as st
import os
import base64

# 1. 페이지 설정
st.set_page_config(page_title="협력사 글로벌 현황", page_icon="🌍", layout="wide")

# 2. CSS 주입 (안전한 문자열 결합)
css = (
    "<style>"
    "@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;800&display=swap');"
    "html, body, [class*='css'] { font-family: 'Noto Sans KR', sans-serif !important; }"
    ".block-container { padding-top: 1.5rem; padding-bottom: 2rem; max-width: 1400px; }"
    "header { visibility: hidden; } footer { visibility: hidden; }"
    ".dashboard-header {"
    "    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);"
    "    padding: 24px 32px; border-radius: 12px; margin-bottom: 30px;"
    "    box-shadow: 0 4px 15px rgba(0,0,0,0.1); color: white;"
    "    display: flex; justify-content: space-between; align-items: center;"
    "}"
    ".dashboard-header h1 { margin: 0; font-size: 28px; font-weight: 800; color: #ffffff; }"
    ".dashboard-header p { margin: 5px 0 0 0; color: #94a3b8; font-size: 15px; }"
    ".info-card {"
    "    background-color: #ffffff; border: 1px solid #cbd5e1;"
    "    border-radius: 12px; padding: 24px; height: 100%; box-shadow: 0 2px 4px rgba(0,0,0,0.02);"
    "}"
    ".info-card-title { font-size: 15px; color: #64748b; font-weight: 700; margin-bottom: 12px; }"
    ".info-card-value { font-size: 17px; color: #0f172a; font-weight: 600; line-height: 1.6; }"
    ".product-card {"
    "    background: white; border: 1px solid #cbd5e1; border-radius: 12px; padding: 30px 20px;"
    "    text-align: center; height: 100%; display: flex; flex-direction: column;"
    "    justify-content: center; align-items: center;"
    "}"
    ".product-title { font-size: 18px; font-weight: 700; color: #1e293b; margin-top: 16px; }"
    ".section-title {"
    "    font-size: 22px; font-weight: 800; color: #0f172a;"
    "    margin-top: 40px; margin-bottom: 20px; padding-bottom: 12px; border-bottom: 2px solid #e2e8f0;"
    "}"
    "[data-testid='stSidebar'] { background-color: #f8fafc; border-right: 1px solid #e2e8f0; }"
    "</style>"
)
st.markdown(css, unsafe_allow_html=True)

# 3. 헤더
st.markdown(
