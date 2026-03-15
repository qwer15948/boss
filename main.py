import streamlit as st
import re

# 1. 페이지 설정
st.set_page_config(page_title="아이온2 정산기", page_icon="🎲", layout="wide")

# 2. 세션 초기화 및 방어 코드
if 'item_data' not in st.session_state:
    st.session_state.item_data = [
        {'name': '필보 아이템', 'price_str': '7,500,000'},
        {'name': '필보 아이템', 'price_str': '7,500,000'}
    ]
else:
    for item in st.session_state.item_data:
        if 'price_str' not in item: item['price_str'] = '0'
        if 'name' not in item: item['name'] = '필보 아이템'

# --- 3. 커스텀 CSS (테두리 고정 및 정렬 최적화) ---
st.markdown("""
    <style>
    .block-container { max-width: 950px; padding-top: 2rem; }
    .main { background-color: #0E1117; }
    
    /* [수정] 카드가 내부 요소를 확실히 감싸도록 설정 */
    .item-card {
        background-color: #262626; 
        padding: 20px; 
        border-radius: 15px;
        border: 1px solid #444; 
        margin-bottom: 15px;
        display: block; /* 영역 확보 */
        overflow: visible;
    }
    
    .item-header-row {
        display: flex; align-items: center; gap: 10px; margin-bottom: 15px;
    }
    .item-badge {
        background-color: #FFB800; color: #000; border-radius: 50%;
        width: 24px; height: 24px; display: flex; align-items: center;
        justify-content: center; font-weight: bold; font-size: 12px; flex-shrink: 0;
    }
    
    /* 입력창 및 버튼 디자인 */
    div[data-testid="stTextInput"] label, div[data-testid="stNumberInput"] label { display: none; }
    input { background-color: #1E1E1E !important; border: 1px solid #444 !important; border-radius: 8px !important; color: white !important; }
    
    /* 삭제 버튼 스타일 정밀 조정 */
    .stButton > button {
        height: 40px; width: 40px; margin-top: 0px !important;
        background-color: #333; border: 1px solid #444; color: #888; border-radius: 8px;
    }
    .stButton > button:hover { border-color: #ff4b4b; color: #ff4b4b; }
    
    /* 결과창 디자인 */
    .result-card {
        background-color: #1E1E1E; padding: 25px; border-radius: 12px;
        border: 1px solid #333; text-align: center; margin-bottom: 15px;
    }
    .summary-box {
        background-color: #161616; padding: 20px; border-radius: 10px; border-left: 4px solid #FFB800;
    }
    .gold-val { color: #FFB800; font-weight: bold; font-size: 28px; }
    .white-val { color: #FFFFFF; font-weight: bold; font-size: 28px; }
    .label-text { color: #888; font-size: 14px; margin-bottom: 5px; }
    hr { border: 0.1px solid #333; margin: 20px 0; }
    </style>
    """, unsafe_allow_html=True)

# --- 유틸리티 함수 ---
def format_comma(val):
    num = re.sub(r'[^0-9]', '', str(val))
    if not num: return "0"
    return f"{int(num):,}"

def add_item():
    st.session_state.item_data.append({'name': '필보 아이템', 'price_str': '0'})

def remove_item(idx):
    if len(st.session_state.item_data) > 1:
        st.session_state.item_data.pop(idx)
        st.rerun()

# --- 화면 구성 ---
st.title("🎲 아이온2 필보 정산기")
st.caption("거래소 수수료 20% | 등록비 2% | 개인 수수료 10%")

col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    st.subheader("📋 입력 정보")
    in_c1, in_c2 = st.columns(2)
    with in_c1:
        st.markdown("<p class='label-text'>👥 참여 인원</p>", unsafe_allow_html=True)
        k = st.number_input("인원", min_value=1, value=6, step=1)
    with in_c2:
        st.markdown("<p class='label-text'>💰 기타 공제액 (원)</p>", unsafe_allow_html=True)
        a = st.number_input("공제", value=0, step=10000, format="%d")

    st.write("---")
    st.write("#### 📦 판매 아이템 리스트")
    
    current_data = []
    for i, item in enumerate(st.session_state.item_data):
        # [핵심] 카드 시작 컨테이너
        with st.container():
            st.markdown(f'<div class="item-card">', unsafe_allow_html=True)
            
            # 1행: 번호 + 이름 + 삭제버튼
            h_col1, h_col2, h_col3 = st.columns([0.8, 8, 1.2])
            with h_col1:
                st.markdown(f'<div style="margin-top:8px;" class="item-badge">{i+1}</div>', unsafe_allow_html=True)
            with h_col2:
                name_val = st.text_input(f"n_{i}", value=item['name'], key=f"ni_{i}")
            with h_col3:
                if st.button("✕", key=f"db_{i}"):
                    remove_item(i)
            
            # 2행: 가격 입력
            st.markdown("<p class='label-text' style='margin-top: 10px;'>판매 가격 (원)</p>", unsafe_allow_html=True)
            price_raw = st.text_input(f"p_{i}", value=item['price_str'], key=f"pi_{i}")
            
            # 데이터 동기화
            formatted_p = format_comma(price_raw)
            current_data.append({'name': name_val, 'price_str': formatted_p})
            
            st.markdown('</div>', unsafe_allow_html=True)
            # 카드 끝
            
    st.session_state.item_data = current_data
    st.button("＋ 아이템 추가", on_click=add_item, use_container_width=True)

# --- 계산 로직 ---
total_sales = sum(int(re.sub(r'[^0-9]', '', it['price_str'])) for it in st.session_state.item_data)
pure_profit = total_sales * 0.78 
listing_price = (pure_profit / (k - 0.12)) - a 
real_share = listing_price * 0.88 

with col_right:
    st.subheader("📊 정산 결과")
    res_c1, res_c2 = st.columns(2)
    with res_c1:
        st.markdown(f'<div class="result-card"><p class="label-text">인당 최종 실수령액</p><p class="gold-val">{max(0, int(real_share)):,}원</p></div>', unsafe_allow_html=True)
    with res_c2:
        st.markdown(f'<div class="result-card"><p class="label-text">팀원 거래소 등록가</p><p class="white-val">{max(0, int(listing_price)):,}원</p></div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="summary-box">
        <div style="display:flex; justify-content:space-between; margin-bottom:10px;"><span class="label-text">📦 총 판매액 합계</span><b>{total_sales:,}원</b></div>
        <div style="display:flex; justify-content:space-between; margin-bottom:10px;"><span class="label-text">💰 판매자 순수 정산금 (0.78T)</span><span>{int(pure_profit):,}원</span></div>
        <hr>
        <div style="display:flex; justify-content:space-between; margin-bottom:10px;"><span style="color:#AAA;">팀원 {k-1}명 총 이체액</span><span>{max(0, int(listing_price * (k-1))):,}원</span></div>
        <div style="display:flex; justify-content:space-between;"><span style="color:#FFB800; font-weight:bold;">판매자 본인 몫 (잔액)</span><span style="color:#FFB800; font-weight:bold;">{max(0, int(pure_profit - (listing_price * (k-1)))):,}원</span></div>
    </div>
    """, unsafe_allow_html=True)