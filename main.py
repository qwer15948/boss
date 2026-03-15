import streamlit as st

# 1. 페이지 설정 (중앙 집중을 위해 layout="wide" 제거)
st.set_page_config(page_title="아이온2 정산기", page_icon="🛡️")

# 2. 세션 초기화
if 'price_list' not in st.session_state:
    st.session_state.price_list = [750, 750]

# --- 3. 커스텀 CSS (너비 제한 및 다크 테마) ---
st.markdown("""
    <style>
    /* 전체 너비 제한 및 중앙 정렬 */
    .block-container {
        max-width: 650px;
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .main { background-color: #0E1117; }
    
    /* 카드 디자인 */
    .result-card {
        background-color: #1E1E1E; padding: 20px; border-radius: 12px;
        border: 1px solid #333; text-align: center; margin-bottom: 15px;
    }
    .summary-box {
        background-color: #161616; padding: 18px; border-radius: 10px;
        border-left: 4px solid #FFB800;
    }
    .gold-val { color: #FFB800; font-weight: bold; font-size: 24px; margin: 5px 0; }
    .white-val { color: #FFFFFF; font-weight: bold; font-size: 24px; margin: 5px 0; }
    .label-text { color: #888; font-size: 13px; }
    
    /* 버튼 스타일 */
    .stButton>button { border-radius: 8px; }
    hr { border: 0.1px solid #333; margin: 15px 0; }
    </style>
    """, unsafe_allow_html=True)

# --- 기능 함수 ---
def add_item():
    st.session_state.price_list.append(0)

def remove_item(idx):
    if len(st.session_state.price_list) > 1:
        st.session_state.price_list.pop(idx)
        st.rerun()

# --- 화면 구성 ---
st.title("🎲 아이온2 필보 정산기")
st.caption("거래소 수수료 20% 등록비 2% 개인 판매 수수료 10%")

# 입력 섹션
with st.container():
    st.subheader("📋 입력 정보")
    col_k, col_a = st.columns(2)
    with col_k:
        k = st.number_input("총 참여 인원", min_value=1, value=6, step=1)
    with col_a:
        a = st.number_input("기타 공제액 (원)", value=0, step=1000)
    
    st.write("#### 💰 판매 아이템")
    new_prices = []
    for i, price in enumerate(st.session_state.price_list):
        item_col, btn_col = st.columns([5, 1])
        with item_col:
            p = st.number_input(f"아이템 {i+1} (만 단위)", value=int(price), key=f"w_price_{i}")
            new_prices.append(p)
        with btn_col:
            st.write("") # 수직 정렬
            st.write("")
            if st.button("🗑️", key=f"w_del_{i}"):
                remove_item(i)
    
    st.session_state.price_list = new_prices
    st.button("➕ 아이템 추가", on_click=add_item, use_container_width=True)

st.markdown("---")

# --- 계산 로직 ---
total_sales = sum(st.session_state.price_list) * 10000
pure_profit = total_sales * 0.78
listing_price = (pure_profit / (k - 0.12)) - a
real_share = listing_price * 0.88

# 결과 섹션 (중앙 집중형 카드)
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
    <div style="display:flex; justify-content:space-between; margin-bottom:5px;">
        <span class="label-text">📦 총 판매액 합계</span>
        <span>{total_sales:,}원</span>
    </div>
    <div style="display:flex; justify-content:space-between; margin-bottom:5px;">
        <span class="label-text">💰 판매자 순수 정산금 (0.78T)</span>
        <span>{int(pure_profit):,}원</span>
    </div>
    <hr>
    <div style="display:flex; justify-content:space-between; margin-bottom:5px;">
        <span style="color:#AAA;">나머지 팀원 ({k-1}명) 총 이체액</span>
        <span>{max(0, int(listing_price * (k-1))):,}원</span>
    </div>
    <div style="display:flex; justify-content:space-between;">
        <span style="color:#FFB800; font-weight:bold;">판매자 본인 몫 (잔액)</span>
        <span style="color:#FFB800; font-weight:bold;">{max(0, int(pure_profit - (listing_price * (k-1)))):,}원</span>
    </div>
</div>
""", unsafe_allow_html=True)