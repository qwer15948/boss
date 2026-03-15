import streamlit as st
import re

# 1. 페이지 설정
st.set_page_config(page_title="아이온2 정산기", page_icon="🎲", layout="wide")

# 2. 세션 초기화
if 'item_data' not in st.session_state:
    st.session_state.item_data = [
        {'name': '필보 아이템', 'price_str': '7,500,000'},
        {'name': '필보 아이템', 'price_str': '7,500,000'}
    ]

# --- 3. 커스텀 CSS ---
st.markdown("""
    <style>
    .block-container { max-width: 950px; padding-top: 2rem; }
    .main { background-color: #0E1117; }
    
    /* 아이템 카드 디자인 */
    .item-card {
        background-color: #262626;
        padding: 15px;
        border-radius: 12px;
        border: 1px solid #333;
        margin-bottom: 12px;
    }
    .item-header-row {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 12px;
    }
    .item-badge {
        background-color: #FFB800; color: #000; border-radius: 50%;
        width: 24px; height: 24px; display: flex; align-items: center;
        justify-content: center; font-weight: bold; font-size: 13px;
        flex-shrink: 0;
    }
    
    /* 입력창 디자인 커스텀 */
    div[data-testid="stTextInput"] label { display: none; }
    
    /* 텍스트 입력창 스타일 */
    input {
        background-color: #1E1E1E !important;
        border: 1px solid #444 !important;
        border-radius: 8px !important;
        color: white !important;
    }
    
    /* 삭제 버튼 스타일 */
    .del-btn-container {
        display: flex;
        justify-content: flex-end;
    }
    .stButton > button {
        height: 32px; width: 32px; padding: 0; border-radius: 8px;
        background-color: #333; border: 1px solid #444; color: #888;
    }
    .stButton > button:hover { border-color: #ff4b4b; color: #ff4b4b; }
    
    /* 결과 박스 디자인 */
    .result-card {
        background-color: #1E1E1E; padding: 20px; border-radius: 12px;
        border: 1px solid #333; text-align: center; margin-bottom: 15px;
    }
    .summary-box {
        background-color: #161616; padding: 18px; border-radius: 10px;
        border-left: 4px solid #FFB800;
    }
    .gold-val { color: #FFB800; font-weight: bold; font-size: 26px; margin: 5px 0; }
    .white-val { color: #FFFFFF; font-weight: bold; font-size: 26px; margin: 5px 0; }
    .label-text { color: #888; font-size: 13px; }
    hr { border: 0.1px solid #333; margin: 15px 0; }
    </style>
    """, unsafe_allow_html=True)

# --- 유틸리티 함수: 실시간 콤마 처리 ---
def format_comma(val):
    # 숫자만 추출
    num = re.sub(r'[^0-9]', '', str(val))
    if not num: return "0"
    return f"{int(num):,}"

# --- 기능 함수 ---
def add_item():
    st.session_state.item_data.append({'name': '필보 아이템', 'price_str': '0'})

def remove_item(idx):
    if len(st.session_state.item_data) > 1:
        st.session_state.item_data.pop(idx)
        st.rerun()

# --- 화면 구성 ---
st.title("🎲 아이온2 필보 정산기")
st.caption("거래소 수수료 20% | 등록비 2% | 개인 수수료 10%")
st.write("")

col_input, col_result = st.columns([1, 1], gap="large")

with col_input:
    st.subheader("📋 입력 정보")
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<p class='label-text'>👥 참여 인원</p>", unsafe_allow_html=True)
        k = st.number_input("인원", min_value=1, value=6, step=1)
    with c2:
        st.markdown("<p class='label-text'>💰 기타 공제액</p>", unsafe_allow_html=True)
        # 공제액도 콤마 처리를 위해 텍스트 입력으로 변경 가능하나, 편의상 기본 유지
        a = st.number_input("공제", value=0, step=10000, format="%d")

    st.write("#### 📦 판매 아이템 리스트")
    
    updated_data = []
    for i, item in enumerate(st.session_state.item_data):
        st.markdown('<div class="item-card">', unsafe_allow_html=True)
        
        # 헤더: [번호] [이름 입력창] [삭제 버튼]
        head_col1, head_col2, head_col3 = st.columns([0.8, 8, 1])
        with head_col1:
            st.markdown(f'<div class="item-badge">{i+1}</div>', unsafe_allow_html=True)
        with head_col2:
            new_name = st.text_input(f"name_{i}", value=item['name'], key=f"n_{i}")
        with head_col3:
            if st.button("✕", key=f"d_{i}"):
                remove_item(i)
        
        # 가격 입력: 실시간 콤마를 위해 text_input 사용
        st.markdown("<p class='label-text' style='margin-bottom: 5px;'>판매 가격 (원)</p>", unsafe_allow_html=True)
        raw_price = st.text_input(f"price_{i}", value=item['price_str'], key=f"p_{i}")
        
        # 입력된 값에서 콤마를 자동으로 찍어주는 로직
        formatted_price = format_comma(raw_price)
        
        updated_data.append({'name': new_name, 'price_str': formatted_price})
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.session_state.item_data = updated_data
    st.button("＋ 아이템 추가", on_click=add_item, use_container_width=True)

# --- 계산 로직 ---
# 콤마 제거 후 숫자로 변환하여 합산
total_sales = sum(int(re.sub(r'[^0-9]', '', item['price_str'])) for item in st.session_state.item_data)
pure_profit = total_sales * 0.78 
listing_price = (pure_profit / (k - 0.12)) - a 
real_share = listing_price * 0.88 

with col_result:
    st.subheader("📊 정산 결과")
    
    res_c1, res_c2 = st.columns(2)
    with res_c1:
        st.markdown(f"""<div class="result-card">
            <p class="label-text">인당 최종 실수령액</p>
            <p class="gold-val">{max(0, int(real_share)):,}원</p>
        </div>""", unsafe_allow_html=True)
    with res_c2:
        st.markdown(f"""<div class="result-card">
            <p class="label-text">팀원 거래소 등록가</p>
            <p class="white-val">{max(0, int(listing_price)):,}원</p>
        </div>""", unsafe_allow_html=True)

    st.markdown(f"""
    <div class="summary-box">
        <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
            <span class="label-text">📦 총 판매액 합계</span>
            <span style="font-weight:bold;">{total_sales:,}원</span>
        </div>
        <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
            <span class="label-text">💰 판매자 순수 정산금 (0.78T)</span>
            <span>{int(pure_profit):,}원</span>
        </div>
        <hr>
        <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
            <span style="color:#AAA;">나머지 팀원 ({k-1}명) 총 이체액</span>
            <span>{max(0, int(listing_price * (k-1))):,}원</span>
        </div>
        <div style="display:flex; justify-content:space-between;">
            <span style="color:#FFB800; font-weight:bold;">판매자 본인 몫 (잔액)</span>
            <span style="color:#FFB800; font-weight:bold;">{max(0, int(pure_profit - (listing_price * (k-1)))):,}원</span>
        </div>
    </div>
    """, unsafe_allow_html=True)