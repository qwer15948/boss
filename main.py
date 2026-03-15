import streamlit as st

# 1. 페이지 설정 (2단 구성을 위해 너비를 조금 넓힘)
st.set_page_config(page_title="아이온2 정산기", page_icon="🎲", layout="wide")

# 2. 세션 초기화
if 'price_list' not in st.session_state:
    st.session_state.price_list = [7500000, 7500000]

# --- 3. 커스텀 CSS (2단 레이아웃 및 디자인) ---
st.markdown("""
    <style>
    /* 전체 너비 제한 및 중앙 정렬 */
    .block-container {
        max-width: 950px;
        padding-top: 2rem;
    }
    .main { background-color: #0E1117; }
    
    /* 아이템 입력 카드 */
    .item-card {
        background-color: #262626;
        padding: 15px;
        border-radius: 12px;
        border: 1px solid #333;
        margin-bottom: 12px;
    }
    .item-header {
        display: flex;
        align-items: center;
        margin-bottom: 10px;
    }
    .item-badge {
        background-color: #FFB800;
        color: #000;
        border-radius: 50%;
        width: 20px;
        height: 20px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        font-size: 11px;
        margin-right: 8px;
    }
    .item-title { color: white; font-weight: bold; font-size: 14px; }
    
    /* 결과 카드 */
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
    
    /* 입력 위젯 스타일 */
    div[data-testid="stNumberInput"] label { display: none; }
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

# --- 상단 타이틀 ---
st.title("🎲 아이온2 필보 정산기")
st.caption("거래소 수수료 20% | 등록비 2% | 개인 수수료 10%")
st.write("")

# --- 메인 레이아웃 (2단 구성) ---
col_input, col_result = st.columns([1, 1], gap="large")

with col_input:
    st.subheader("📋 입력 정보")
    
    # 인원 및 공제액 (한 줄 배치)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<p class='label-text'>👥 참여 인원</p>", unsafe_allow_html=True)
        k = st.number_input("인원", min_value=1, value=6, step=1, key="k_val")
    with c2:
        st.markdown("<p class='label-text'>💰 기타 공제액</p>", unsafe_allow_html=True)
        a = st.number_input("공제", value=0, step=10000, key="a_val", format="%d")

    st.write("#### 📦 판매 아이템 리스트")
    
    new_prices = []
    for i, price in enumerate(st.session_state.price_list):
        st.markdown(f"""<div class="item-card"><div class="item-header"><div class="item-badge">{i+1}</div><div class="item-title">필보 아이템</div></div>""", unsafe_allow_html=True)
        
        v_col, d_col = st.columns([5, 1])
        with v_col:
            # format="%d"와 step 설정을 통해 천 단위 콤마 표시
            p = st.number_input(f"p_{i}", value=int(price), key=f"p_{i}", step=10000, format="%d")
            new_prices.append(p)
        with d_col:
            st.write("") 
            if st.button("✕", key=f"del_{i}"):
                remove_item(i)
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.session_state.price_list = new_prices
    st.button("＋ 아이템 추가", on_click=add_item, use_container_width=True)

# --- 계산 로직 ---
total_sales = sum(st.session_state.price_list)
pure_profit = total_sales * 0.78 
listing_price = (pure_profit / (k - 0.12)) - a 
real_share = listing_price * 0.88 

with col_result:
    st.subheader("📊 정산 결과")
    
    # 결과 카드 2개 나란히
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

    # 상세 요약 박스
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
            <span style="color:#AAA;">팀원 {k-1}명 총 이체액</span>
            <span>{max(0, int(listing_price * (k-1))):,}원</span>
        </div>
        <div style="display:flex; justify-content:space-between;">
            <span style="color:#FFB800; font-weight:bold;">판매자 본인 몫 (잔액)</span>
            <span style="color:#FFB800; font-weight:bold;">{max(0, int(pure_profit - (listing_price * (k-1)))):,}원</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.write("")
    st.info("💡 위 정산 결과를 스크린샷 찍어 팀원들에게 공유하세요.")