import streamlit as st

# 1. 페이지 설정 및 초기화 (반드시 최상단)
st.set_page_config(page_title="아이온2 정산기", layout="wide")

# 세션 상태 초기화 로직 (None 방지)
if 'items' not in st.session_state:
    st.session_state.items = {0: 750, 1: 750}  # {ID: 가격} 형태
if 'next_id' not in st.session_state:
    st.session_state.next_id = 2

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

# --- 콜백 함수 (에러 방지용 핵심 로직) ---
def add_item():
    st.session_state.items[st.session_state.next_id] = 0
    st.session_state.next_id += 1

def remove_item(item_id):
    if len(st.session_state.items) > 1:
        del st.session_state.items[item_id]

# --- 화면 레이아웃 ---
st.title("🛡️ ION2 Settlement Helper")

col_left, col_right = st.columns([1, 1.2], gap="large")

with col_left:
    st.subheader("📋 입력 정보")
    
    k = st.number_input("총 참여 인원", min_value=1, value=6, step=1)
    a = st.number_input("기타 공제액 (원 단위)", value=0, step=1000)
    
    st.write("---")
    st.write("#### 💰 판매 아이템 리스트")
    
    # 세션 딕셔너리를 직접 순회하며 입력창 생성
    for item_id in list(st.session_state.items.keys()):
        item_col, btn_col = st.columns([4, 1])
        with item_col:
            # 입력값이 즉시 세션에 저장되도록 구성
            st.session_state.items[item_id] = st.number_input(
                f"아이템 가격 (만 단위)", 
                value=st.session_state.items[item_id], 
                key=f"input_{item_id}"
            )
        with btn_col:
            st.write(" ")
            st.write(" ")
            # 삭제 버튼 (on_click 대신 직접 호출 시 rerun 필요없음)
            if st.button("🗑️", key=f"del_{item_id}"):
                remove_item(item_id)
                st.rerun()
    
    st.button("➕ 아이템 추가", on_click=add_item, use_container_width=True)

# --- 계산 로직 ---
# 총 판매액 합산
total_sales = sum(st.session_state.items.values()) * 10000
# 판매자 정산 (80% 정산 - 2% 등록비 = 78%)
pure_profit = total_sales * 0.78
# 팀원 등록가 역산 공식 (공평하게 수수료를 분담하는 P 값)
listing_price = (pure_profit / (k - 0.12)) - a
# 팀원 실수령 (등록가에서 수수료 10% 및 등록비 2% 제외 = 88%)
real_share = listing_price * 0.88

# --- 결과 화면 ---
with col_right:
    st.subheader("📊 정산 결과 요약")
    
    res_c1, res_c2 = st.columns(2)
    with res_c1:
        st.markdown(f"""<div class="result-card">
            <p style="color:#888; font-size:14px; margin:0;">인당 최종 실수령액</p>
            <p class="gold-val">{max(0, int(real_share)):,}원</p>
            <p style="color:#555; font-size:11px; margin:0;">모든 수수료/등록비 제외</p>
        </div>""", unsafe_allow_html=True)
    
    with res_c2:
        st.markdown(f"""<div class="result-card">
            <p style="color:#888; font-size:14px; margin:0;">팀원 거래소 등록가</p>
            <p class="white-val">{max(0, int(listing_price)):,}원</p>
            <p style="color:#555; font-size:11px; margin:0;">잡동사니 올리는 가격</p>
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