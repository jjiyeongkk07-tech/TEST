import streamlit as st
import os
import base64

# 1. 페이지 기본 설정
st.set_page_config(page_title="협력사 글로벌 현황", page_icon="🌍", layout="wide")

# 2. 폰트 및 프리미엄 C-Level CSS 주입
st.markdown("""
    <style>
        /* Noto Sans KR 폰트 임포트 */
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;800&display=swap');

        /* 글로벌 폰트 강제 적용 */
        * { font-family: 'Noto Sans KR', sans-serif !important; }

        /* 기본 여백 최소화 및 불필요한 요소 숨김 */
        .block-container { padding-top: 1.5rem; padding-bottom: 2rem; max-width: 1400px; }
        header { visibility: hidden; }
        footer { visibility: hidden; }

        /* 대시보드 헤더 배너 */
        .dashboard-header {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            padding: 24px 32px;
            border-radius: 12px;
            margin-bottom: 30px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            color: white;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .dashboard-header h1 { margin: 0; font-size: 28px; font-weight: 800; color: #ffffff; letter-spacing: -0.5px;}
        .dashboard-header p { margin: 5px 0 0 0; color: #94a3b8; font-size: 15px; font-weight: 400;}

        /* 정보 카드 (거점 현황) 스타일 */
        .info-card {
            background-color: #ffffff;
            border: 1px solid #cbd5e1;
            border-radius: 12px;
            padding: 24px;
            height: 100%;
            box-shadow: 0 2px 4px rgba(0,0,0,0.02);
            transition: all 0.2s ease-in-out;
        }
        .info-card:hover { box-shadow: 0 6px 12px rgba(0,0,0,0.08); transform: translateY(-2
