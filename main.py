import streamlit as st

# 1. 페이지 설정
st.set_page_config(page_title="아이온2 정산기", layout="wide")

# 2. 세션 초기화 (에러 방지용 안전 장치)
if 'price_list' not in st.session_state:
    st.session_state.price_list = [750, 750]  # 가격만 저장하는 리스트

# --- 스타일링 ---
st.markdown("""
    <style>
    .main { background-color: #0E1117; }
    .result-card {
        background-color: #1E1E1E; padding: 25px; border-radius: 15px;
        border: 1px solid #333; text-align: center; margin-bottom: 20px;
    }
    .summary-box {
        background-color: #161616; padding: 20px; border-radius: 10px;
        border-left: 5px solid #FFB800;
    }
    .gold-val { color: #FFB800; font-weight: bold; font-size: 28px; margin: 10px 0; }
    .white-val { color: #FFFFFF; font-weight: bold; font-size: 28px; margin: 10px 0; }
    hr { border: 0.1px solid #444; margin: 20px 0; }
    </style>
    """, unsafe_allow_html=True)

# --- 기능 함수 ---
def add_item():
    st.session_state.price_list.append(0)

def remove_item(idx):
    if len(st.session_state.price_list) > 1:
        st.session_state.price_list.pop(idx)
        st.rerun()

# --- 화면 레이아웃 ---
st.title("🛡️ ION2 Settlement Helper")

col_left, col_right = st.columns([1, 1.2], gap="large")

with col_left:
    st.subheader("📋 입력 정보")
    
    k = st.number_input("총 참여 인원", min_value=1, value=6, step=1)
    a = st.number_input("기타 공제액 (원 단위)", value=0, step=1000)
    
    st.write("---")
    st.write("#### 💰 판매 아이템 리스트")
    
    # [에러 방지] 리스트를 직접 순회하며 값 업데이트
    new_prices = []
    for i, price in enumerate(st.session_state.price_list):
        item_col, btn_col = st.columns([4, 1])
        with item_col:
            # key 이름을 데이터 변수명과 다르게 설정하여 충돌 방지
            p = st.number_input(f"아이템 {i+1} 가격 (만 단위)", 
                                value=int(price), 
                                key=f"widget_price_{i}")
            new_prices.append(p)
        with btn_col:
            st.write(" ")
            st.write(" ")
            if st.button("🗑️", key=f"widget_del_{i}"):
                remove_item(i)
    
    # 입력된 값들을 세션에 다시 저장
    st.session_state.price_list = new_prices
    
    st.button("➕ 아이템 추가", on_click=add_item, use_container_width=True)

# --- 계산 로직 ---
total_sales = sum(st.session_state.price_list) * 10000
pure_profit = total_sales * 0.78
listing_price = (pure_profit / (k - 0.12)) - a
real_share = listing_price * 0.88

# --- 결과 화면 ---
with col_right:
    st.subheader("📊 정산 결과 요약")
    
    res_c1, res_c2 = st.columns(2)
    with res_c1:
        st.markdown(f"""<div class="result-card">
            <p style="color:#888; font-size:14px; margin:0;">인당 최종 실수령액</p>
            <p class="gold-val">{max(0, int(real_share)):,}원</p>
        </div>""", unsafe_allow_html=True)
    
    with res_c2:
        st.markdown(f"""<div class="result-card">
            <p style="color:#888; font-size:14px; margin:0;">팀원 거래소 등록가</p>
            <p class="white-val">{max(0, int(listing_price)):,}원</p>
        </div>""", unsafe_allow_html=True)

    st.markdown(f"""
    <div class="summary-box">
        <p><b>📦 총 판매액:</b> {total_sales:,}원</p>
        <p><b>💰 판매자 순수 정산금:</b> {int(pure_profit):,}원</p>
        <hr>
        <div style="display:flex; justify-content:space-between; margin-bottom:5px;">
            <span style="color:#AAA;">팀원 {k-1}명 총 이체액</span>
            <span>{max(0, int(listing_price * (k-1))):,}원</span>
        </div>
        <div style="display:flex; justify-content:space-between;">
            <span style="color:#FFB800; font-weight:bold;">판매자 본인 몫 (잔액)</span>
            <span style="color:#FFB800; font-weight:bold;">{max(0, int(pure_profit - (listing_price * (k-1)))):,}원</span>
        </div>
    </div>
    """, unsafe_allow_html=True)