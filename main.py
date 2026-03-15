import streamlit as st

# 1. 페이지 설정 및 초기화 (최상단 배치)
st.set_page_config(page_title="아이온2 정산기", layout="wide")

# 세션 상태가 비어있을 경우를 대비한 안전한 초기화
if 'items' not in st.session_state:
    st.session_state.items = [{'id': 0, 'value': 750}, {'id': 1, 'value': 750}]
if 'next_id' not in st.session_state:
    st.session_state.next_id = 2

# --- 스타일링 ---
st.markdown("""
    <style>
    .main { background-color: #0E1117; }
    div[data-testid="stNumberInput"] label { color: #AAAAAA !important; font-size: 14px; }
    .result-card {
        background-color: #1E1E1E;
        padding: 25px;
        border-radius: 15px;
        border: 1px solid #333;
        text-align: center;
        margin-bottom: 20px;
    }
    .summary-box {
        background-color: #161616;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #FFB800;
    }
    .gold-val { color: #FFB800; font-weight: bold; font-size: 28px; margin: 10px 0; }
    .white-val { color: #FFFFFF; font-weight: bold; font-size: 28px; margin: 10px 0; }
    hr { border: 0.1px solid #444; margin: 20px 0; }
    </style>
    """, unsafe_allow_html=True)

# --- 데이터 조작 함수 ---
def add_item():
    st.session_state.items.append({'id': st.session_state.next_id, 'value': 0})
    st.session_state.next_id += 1

def remove_item(item_id):
    if len(st.session_state.items) > 1:
        # ID를 기준으로 해당 아이템 삭제
        st.session_state.items = [item for item in st.session_state.items if item['id'] != item_id]
        st.rerun()

# --- 화면 레이아웃 ---
st.title("🛡️ ION2 Settlement Helper")
st.caption("판매자(22% 차감) & 팀원(12% 차감) 수수료 완전 보정")

col_left, col_right = st.columns([1, 1.2], gap="large")

with col_left:
    st.subheader("📋 입력 정보")
    
    k = st.number_input("총 참여 인원", min_value=1, value=6, step=1)
    a = st.number_input("기타 공제액 (원 단위)", value=0, step=1000)
    
    st.write("---")
    st.write("#### 💰 판매 아이템 리스트")
    
    # 세션에 저장된 리스트를 안전하게 순회
    current_items = st.session_state.items
    for i, item in enumerate(current_items):
        item_col, btn_col = st.columns([4, 1])
        with item_col:
            # 개별 아이템 가격 입력 (ID 기반 고유 Key 사용)
            item['value'] = st.number_input(
                f"아이템 {i+1} 가격 (만 단위)", 
                value=item['value'], 
                key=f"input_{item['id']}"
            )
        with btn_col:
            st.write(" ") # 레이아웃 정렬용
            st.write(" ")
            if st.button("🗑️", key=f"del_{item['id']}"):
                remove_item(item['id'])
    
    st.button("➕ 아이템 추가", on_click=add_item, use_container_width=True)

# --- 계산 로직 ---
# 총 판매액 (만원 단위 -> 원 단위)
total_sales = sum(item['value'] for item in st.session_state.items) * 10000
# 판매자 순수익 (거래소 80% 정산 - 등록비 2% = 78%)
pure_profit = total_sales * 0.78
# 팀원 등록 가격 (공식: P = pure_profit / (k - 0.12) - a)
listing_price = (pure_profit / (k - 0.12)) - a
# 팀원 최종 실수령 (등록가에서 수수료 10% 및 등록비 2% 제외 = 88%)
real_share = listing_price * 0.88

# --- 결과 화면 ---
with col_right:
    st.subheader("📊 정산 결과 요약")
    
    res_c1, res_c2 = st.columns(2)
    with res_c1:
        st.markdown(f"""<div class="result-card">
            <p style="color:#888; font-size:14px; margin:0;">인당 최종 실수령액</p>
            <p class="gold-val">{int(max(0, real_share)):,}원</p>
            <p style="color:#555; font-size:11px; margin:0;">등록비/수수료 모두 제외</p>
        </div>""", unsafe_allow_html=True)
    
    with res_c2:
        st.markdown(f"""<div class="result-card">
            <p style="color:#888; font-size:14px; margin:0;">팀원 거래소 등록가</p>
            <p class="white-val">{int(max(0, listing_price)):,}원</p>
            <p style="color:#555; font-size:11px; margin:0;">이 금액으로 올리라고 하세요</p>
        </div>""", unsafe_allow_html=True)

    st.markdown(f"""
    <div class="summary-box">
        <p style="margin-bottom:8px;"><b>📦 아이템 합계:</b> {total_sales:,}원</p>
        <p style="margin-bottom:8px;"><b>💰 판매자 순수 정산금:</b> {int(pure_profit):,}원</p>
        <hr style="margin:10px 0;">
        <div style="display:flex; justify-content:space-between; margin-bottom:5px;">
            <span style="color:#AAA;">팀원 ({k-1}명) 총 이체액</span>
            <span>{int(max(0, listing_price * (k-1))):,}원</span>
        </div>
        <div style="display:flex; justify-content:space-between; margin-bottom:5px;">
            <span style="color:#FFB800; font-weight:bold;">판매자 본인 몫 (잔액)</span>
            <span style="color:#FFB800; font-weight:bold;">{int(max(0, pure_profit - (listing_price * (k-1)))):,}원</span>
        </div>
    </div>
    """, unsafe_allow_html=True)