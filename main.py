import streamlit as st

# 1. 페이지 설정
st.set_page_config(page_title="아이온2 정산기", page_icon="🎲", layout="wide")

# 2. 세션 초기화
if 'item_data' not in st.session_state:
    st.session_state.item_data = [
        {'name': '필보 아이템', 'price': 7500000},
        {'name': '필보 아이템', 'price': 7500000}
    ]

# --- 3. 커스텀 CSS (레이아웃 정밀 조정) ---
st.markdown("""
    <style>
    .block-container { max-width: 950px; padding-top: 2rem; }
    .main { background-color: #0E1117; }
    
    /* 아이템 카드 디자인 */
    .item-card {
        background-color: #262626;
        padding: 12px 15px;
        border-radius: 12px;
        border: 1px solid #333;
        margin-bottom: 10px;
    }
    .item-header {
        display: flex;
        align-items: center;
        margin-bottom: 8px;
    }
    .item-badge {
        background-color: #FFB800; color: #000; border-radius: 50%;
        width: 18px; height: 18px; display: flex; align-items: center;
        justify-content: center; font-weight: bold; font-size: 10px; margin-right: 8px;
    }
    
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
    
    /* 입력창 및 버튼 높이 맞춤 */
    div[data-testid="stNumberInput"] label, div[data-testid="stTextInput"] label { display: none; }
    .stButton > button {
        margin-top: 0px !important;
        height: 42px; /* 입력창 높이와 일치시킴 */
        width: 100%;
        border-radius: 8px;
        border: 1px solid #444;
        background-color: #333;
        color: #888;
    }
    .stButton > button:hover {
        border-color: #ff4b4b;
        color: #ff4b4b;
    }
    hr { border: 0.1px solid #333; margin: 15px 0; }
    </style>
    """, unsafe_allow_html=True)

# --- 기능 함수 ---
def add_item():
    st.session_state.item_data.append({'name': '필보 아이템', 'price': 0})

def remove_item(idx):
    if len(st.session_state.item_data) > 1:
        st.session_state.item_data.pop(idx)
        st.rerun()

# --- 상단 타이틀 ---
st.title("🎲 아이온2 필보 정산기")
st.caption("거래소 수수료 20% | 등록비 2% | 개인 수수료 10%")
st.write("")

# --- 메인 레이아웃 (2단 구성) ---
col_input, col_result = st.columns([1, 1], gap="large")

with col_input:
    st.subheader("📋 입력 정보")
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<p class='label-text'>👥 참여 인원</p>", unsafe_allow_html=True)
        k = st.number_input("인원", min_value=1, value=6, step=1, key="k_val")
    with c2:
        st.markdown("<p class='label-text'>💰 기타 공제액</p>", unsafe_allow_html=True)
        a = st.number_input("공제", value=0, step=10000, key="a_val", format="%d")

    st.write("#### 📦 판매 아이템 리스트")
    
    updated_data = []
    for i, item in enumerate(st.session_state.item_data):
        st.markdown(f"""<div class="item-card"><div class="item-header"><div class="item-badge">{i+1}</div></div>""", unsafe_allow_html=True)
        
        # 컬럼 비율 조정 (이름:가격:삭제 = 3:6:1)
        name_col, price_col, del_col = st.columns([3, 6, 1])
        with name_col:
            new_name = st.text_input(f"name_{i}", value=item['name'], key=f"name_{i}", placeholder="보스 이름")
        with price_col:
            # format="%d"를 통해 숫자 입력 시 콤마 표시
            new_price = st.number_input(f"price_{i}", value=int(item['price']), key=f"price_{i}", step=10000, format="%d")
        with del_col:
            # 삭제 버튼의 높이를 입력창과 맞춤
            if st.button("✕", key=f"del_{i}"):
                remove_item(i)
        
        updated_data.append({'name': new_name, 'price': new_price})
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.session_state.item_data = updated_data
    st.button("＋ 아이템 추가", on_click=add_item, use_container_width=True)

# --- 계산 로직 ---
total_sales = sum(item['price'] for item in st.session_state.item_data)
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
    
    st.write("")
    st.info("💡 보스 이름을 수정하고 가격을 입력하면 결과가 즉시 반영됩니다.")