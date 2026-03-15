import streamlit as st

# 페이지 기본 설정
st.set_page_config(page_title="아이온2 정산기", layout="wide")

# --- 1. 스타일링 (이미지 디자인 재현) ---
st.markdown("""
    <style>
    .main { background-color: #0E1117; }
    .stNumberInput div div input { background-color: #1E1E1E !important; color: white !important; border-radius: 8px !important; }
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
    .gold-val { color: #FFB800; font-weight: bold; font-size: 28px; }
    .white-val { color: #FFFFFF; font-weight: bold; font-size: 28px; }
    .label-text { color: #888888; font-size: 14px; margin-bottom: 5px; }
    hr { border: 0.1px solid #333; margin: 20px 0; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 데이터 관리 (아이템 동적 추가/삭제) ---
if 'items' not in st.session_state:
    st.session_state.items = [750, 750]  # 초기 아이템 2개

def add_item():
    st.session_state.items.append(0)

def remove_item(index):
    if len(st.session_state.items) > 1:
        st.session_state.items.pop(index)
        st.rerun()

# --- 3. UI 레이아웃 ---
st.title("🛡️ ION2 Field Boss Settlement")
st.caption("판매자(2%+20%) 및 팀원(2%+10%) 수수료 완벽 보정 시스템")

col_left, col_right = st.columns([1, 1.2], gap="large")

with col_left:
    st.subheader("📋 입력 정보")
    
    # 인원 및 추가금
    c1, c2 = st.columns(2)
    with c1:
        k = st.number_input("총 참여 인원", min_value=1, value=6, step=1)
    with c2:
        a = st.number_input("기타 공제액 (원)", value=0, step=1000)
    
    st.write("---")
    st.write("#### 💰 판매 아이템 리스트")
    
    # 아이템 입력창들 생성
    new_items = []
    for i, val in enumerate(st.session_state.items):
        item_col, btn_col = st.columns([4, 1])
        with item_col:
            v = st.number_input(f"{i+1}번 아이템 가격 (만 단위)", value=val, key=f"item_{i}")
            new_items.append(v)
        with btn_col:
            st.write("") # 간격 맞추기
            if st.button("🗑️", key=f"del_{i}"):
                remove_item(i)
    
    st.session_state.items = new_items

    if st.button("➕ 아이템 추가", on_click=add_item, use_container_width=True):
        pass

# --- 4. 계산 로직 ---
total_sales = sum(st.session_state.items) * 10000
# 판매자 순수익 (0.78T)
pure_profit = total_sales * 0.78
# 팀원 등록가 (P) - 추가 공제액 a 반영
listing_price = (pure_profit / (k - 0.12)) - a
# 최종 실수령액 (X = 0.88P)
real_share = listing_price * 0.88

# --- 5. 결과 화면 ---
with col_right:
    st.subheader("📊 정산 결과 요약")
    
    # 카드형 지표
    res_c1, res_c2 = st.columns(2)
    with res_c1:
        st.markdown(f"""<div class="result-card">
            <p class="label-text">인당 최종 실수령액</p>
            <p class="gold-val">{int(real_share):,}원</p>
            <p style="color:#555; font-size:12px;">모든 수수료 제외 후 가방에 들어올 돈</p>
        </div>""", unsafe_allow_html=True)
    
    with res_c2:
        st.markdown(f"""<div class="result-card">
            <p class="label-text">팀원 거래소 등록가</p>
            <p class="white-val">{int(listing_price):,}원</p>
            <p style="color:#555; font-size:12px;">팀원들이 잡동사니 올릴 금액</p>
        </div>""", unsafe_allow_html=True)

    # 상세 내역 박스
    st.markdown(f"""
    <div class="summary-box">
        <p style="margin-bottom:10px;"><b>아이템 합계:</b> {total_sales:,}원</p>
        <p style="margin-bottom:10px;"><b>판매자 순수 정산금:</b> {int(pure_profit):,}원 <span style="font-size:11px; color:#888;">(80%정산 - 2%등록비)</span></p>
        <hr>
        <div style="display:flex; justify-content:space-between; margin-bottom:5px;">
            <span>나머지 팀원 ({k-1}명) 총 이체액</span>
            <span>{int(listing_price * (k-1)):,}원</span>
        </div>
        <div style="display:flex; justify-content:space-between; margin-bottom:5px;">
            <span style="color:#FFB800;">판매자 본인 몫 (잔액)</span>
            <span style="color:#FFB800; font-weight:bold;">{int(pure_profit - (listing_price * (k-1))):,}원</span>
        </div>
        <div style="display:flex; justify-content:space-between;">
            <span style="color:#FFB800;">팀원 개별 실수령액</span>
            <span style="color:#FFB800; font-weight:bold;">{int(real_share):,}원</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.warning("⚠️ 팀원들은 반드시 등록비 2%가 본인 부담임을 인지해야 합니다.")