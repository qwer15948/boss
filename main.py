import streamlit as st

# 1. 페이지 설정
st.set_page_config(page_title="아이온2 정산기", page_icon="🛡️")

# 2. 세션 초기화
if 'price_list' not in st.session_state:
    st.session_state.price_list = [7500000, 7500000] # 만 단위가 아닌 원 단위로 기본값 설정

# --- 3. 커스텀 CSS (카드 디자인 강화) ---
st.markdown("""
    <style>
    .block-container { max-width: 600px; padding-top: 2rem; }
    .main { background-color: #0E1117; }
    
    /* 아이템 입력 카드 */
    .item-card {
        background-color: #262626;
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #333;
        margin-bottom: 15px;
        position: relative;
    }
    .item-header {
        display: flex;
        align-items: center;
        margin-bottom: 15px;
    }
    .item-badge {
        background-color: #FFB800;
        color: #000;
        border-radius: 50%;
        width: 22px;
        height: 22px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        font-size: 12px;
        margin-right: 10px;
    }
    .item-title {
        color: white;
        font-weight: bold;
        font-size: 16px;
    }
    
    /* 결과 카드 및 박스 */
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
    
    /* 입력창 라벨 숨기기 및 스타일 */
    div[data-testid="stNumberInput"] label { display: none; }
    hr { border: 0.1px solid #333; margin: 20px 0; }
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
st.caption("거래소 수수료 20% | 등록비 2% | 개인 수수료 10%")

# 상단 인원 설정 섹션
with st.container():
    col_k, col_a = st.columns(2)
    with col_k:
        st.write("👥 **참여 인원**")
        k = st.number_input("인원", min_value=1, value=6, step=1, key="total_people")
    with col_a:
        st.write("💰 **기타 공제액**")
        a = st.number_input("공제", value=0, step=1000, key="extra_minus")

st.write("---")
st.write("#### 📦 판매 아이템 리스트")

# 아이템 입력 섹션 (카드 형식)
new_prices = []
for i, price in enumerate(st.session_state.price_list):
    # HTML로 카드 시작
    st.markdown(f"""
        <div class="item-card">
            <div class="item-header">
                <div class="item-badge">{i+1}</div>
                <div class="item-title">필보 아이템</div>
            </div>
    """, unsafe_allow_html=True)
    
    # 카드 내부 입력을 위한 컬럼
    val_col, unit_col, del_col = st.columns([10, 1, 2])
    with val_col:
        p = st.number_input(f"가격_{i}", value=int(price), key=f"w_price_{i}", step=10000)
    with unit_col:
        st.markdown("<p style='margin-top:10px; color:#888;'>원</p>", unsafe_allow_html=True)
    with del_col:
        if st.button("✕", key=f"w_del_{i}"):
            remove_item(i)
    
    st.markdown("</div>", unsafe_allow_html=True) # 카드 종료
    new_prices.append(p)

st.session_state.price_list = new_prices
st.button("＋ 아이템 추가", on_click=add_item, use_container_width=True)

st.write("")
st.write("")

# --- 계산 로직 ---
total_sales = sum(st.session_state.price_list)
pure_profit = total_sales * 0.78 # 판매자 순이익
listing_price = (pure_profit / (k - 0.12)) - a # 팀원 등록가
real_share = listing_price * 0.88 # 팀원 실수령

# --- 결과 섹션 ---
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