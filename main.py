import streamlit as st
import re

st.set_page_config(page_title="아이온2 정산기", page_icon="🎲", layout="wide")

if 'item_count' not in st.session_state:
    st.session_state['ni_0'] = '필보'
    st.session_state['pi_0'] = '7,500,000'

st.markdown("""
    <style>
    .block-container { max-width: 950px; padding-top: 2rem; }
    
    /* 카드 컨테이너 */
    div[data-testid="stVerticalBlockBorderWrapper"]:has(.item-card-marker) {
        background-color: #262626 !important;
        padding: 20px !important;
        border-radius: 12px !important;
        border: 1px solid #333 !important;
        margin-bottom: 15px !important;
    }

    /* 삭제 버튼 전용 (완전 초기화 후 재정의) */
    button[key^="del_"] {
        all: unset !important;
        box-sizing: border-box !important;
        width: 42px !important;
        height: 42px !important;
        min-width: 42px !important;
        max-width: 42px !important;
        background-color: #333 !important;
        border: 1px solid #444 !important;
        color: #888 !important;
        border-radius: 8px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-size: 18px !important;
        cursor: pointer !important;
        transition: 0.2s !important;
    }
    button[key^="del_"]:hover {
        background-color: #452a2a !important;
        border-color: #ff4b4b !important;
        color: #ff4b4b !important;
    }

    /* 추가 버튼 전용 */
    button[key="add_btn"] {
        all: unset !important;
        box-sizing: border-box !important;
        width: 100% !important;
        height: 50px !important;
        background-color: #333 !important;
        border: 1px solid #FFB800 !important;
        color: #FFB800 !important;
        border-radius: 10px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-weight: bold !important;
        cursor: pointer !important;
    }
    
    /* 기타 UI 생략 (기존 스타일 유지) */
    .label-box { color: #AAA; font-size: 14px; font-weight: bold; display: flex; align-items: center; height: 42px; }
    .item-badge {
        background-color: #FFB800; color: #000; border-radius: 50%;
        width: 22px; height: 22px; display: flex; align-items: center;
        justify-content: center; font-weight: bold; font-size: 11px;
        margin-top: 10px;
    }
    div[data-testid="stTextInput"] label { display: none !important; }
    input { background-color: #1E1E1E !important; border: 1px solid #444 !important; border-radius: 8px !important; color: white !important; }
    .result-card { background-color: #1E1E1E; padding: 25px; border-radius: 12px; border: 1px solid #333; text-align: center; margin-bottom: 15px; }
    .gold-val { color: #FFB800; font-weight: bold; font-size: 20px; }
    .white-val { color: #FFFFFF; font-weight: bold; font-size: 20px; }
    .summary-box { background-color: #161616; padding: 20px; border-radius: 10px; border-left: 4px solid #FFB800; }
    </style>
""", unsafe_allow_html=True)

# --- 이하 로직 (사용자 원본과 동일) ---
def format_comma(val):
    num = re.sub(r'[^0-9]', '', str(val))
    return f"{int(num):,}" if num else "0"

def on_price_change(idx):
    key = f"pi_{idx}"
    if key in st.session_state:
        st.session_state[key] = format_comma(st.session_state[key])

def add_item():
    existing_indices = [int(k.split('_')[1]) for k in st.session_state.keys() if k.startswith('ni_')]
    next_idx = max(existing_indices) + 1 if existing_indices else 0
    st.session_state[f'ni_{next_idx}'] = '필보'
    st.session_state[f'pi_{next_idx}'] = '0'

st.title("🎲 아이온2 필보 정산기")
st.caption("거래소 수수료 20% | 등록 수수료 2% | 개인 판매 수수료 10%")

col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    in_c1, in_c2 = st.columns(2)
    with in_c1: k = st.number_input("👥 참여 인원", min_value=1, value=6, step=1)
    with in_c2: a = st.number_input("💰 기타 공제액", value=0, step=10000, format="%d")
    st.write("---")
    st.write("#### 📦 판매 아이템 리스트")
    
    item_indices = sorted([int(k.split('_')[1]) for k in st.session_state.keys() if k.startswith('ni_')])
    display_num = 1
    for i in item_indices:
        if f'ni_{i}' not in st.session_state: continue
        with st.container(border=True):
            st.markdown('<div class="item-card-marker"></div>', unsafe_allow_html=True)
            r1_c1, r1_c2, r1_c3 = st.columns([1, 8, 1], gap="small") # 비율 조정 및 gap 추가
            with r1_c1: st.markdown(f'<div class="item-badge">{display_num}</div>', unsafe_allow_html=True)
            with r1_c2: st.text_input("보스명", key=f"ni_{i}")
            with r1_c3:
                if st.button("✕", key=f"del_{i}"):
                    del st.session_state[f'ni_{i}']
                    del st.session_state[f'pi_{i}']
                    st.rerun()
            r2_c1, r2_c2, r2_c3 = st.columns([2, 7, 1])
            with r2_c1: st.markdown('<div class="label-box">판매가</div>', unsafe_allow_html=True)
            with r2_c2: st.text_input("가격", key=f"pi_{i}", on_change=on_price_change, args=(i,))
            with r2_c3: st.markdown('<div class="label-box">원</div>', unsafe_allow_html=True)
            display_num += 1

    st.button("＋ 아이템 추가", key="add_btn", on_click=add_item)

# 계산 로직 및 결과 화면 (원본 유지)
total_sales = 0
current_pi_keys = [k for k in st.session_state.keys() if k.startswith('pi_')]
for pk in current_pi_keys:
    val = re.sub(r'[^0-9]', '', st.session_state[pk])
    total_sales += int(val) if val else 0

pure_profit = total_sales * 0.78 
listing_price = (pure_profit / (k - 0.12)) - a 
real_share = listing_price * 0.88 

with col_right:
    st.subheader("📊 정산 결과")
    res_c1, res_c2 = st.columns(2)
    with res_c1: st.markdown(f'<div class="result-card"><p style="color:#888; font-size: 13px;">인당 최종 실수령액</p><p class="gold-val">{max(0, int(real_share)):,}원</p></div>', unsafe_allow_html=True)
    with res_c2: st.markdown(f'<div class="result-card"><p style="color:#888; font-size: 13px;">팀원 거래소 등록가</p><p class="white-val">{max(0, int(listing_price)):,}원</p></div>', unsafe_allow_html=True)
    
    copy_text = f"💎 아이온2 필보 정산 결과\n- 거래소 등록가: {max(0, int(listing_price)):,}원\n- 인당 실수령액: {max(0, int(real_share)):,}원"
    st.code(copy_text, language=None)