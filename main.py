import streamlit as st
import time

# 페이지 기본 설정
st.set_page_config(page_title="아이온2 정산기", layout="wide")

# --- 1. 스타일링 ---
st.markdown("""
    <style>
    .main { background-color: #0E1117; }
    div[data-testid="stNumberInput"] label { color: #AAAAAA !important; }
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
    hr { border: 0.1px solid #444; margin: 20px 0; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 데이터 관리 (에러 방지를 위한 고유 ID 방식) ---
if 'items' not in st.session_state:
    # 초기 아이템 세팅 (id는 고유값, value는 가격)
    st.session_state.items = [{'id': 0, 'value': 750}, {'id': 1, 'value': 750}]
    st.session_state.next_id = 2

def add_item():
    st.session_state.items.append({'id': st.session_state.next_id, 'value': 0})
    st.session_state.next_id += 1

def remove_item(idx):
    if len(st.session_state.items) > 1:
        st.session_state.items.pop(idx)
        st.rerun()

# --- 3. UI 레이아웃 ---
st.title("🛡️ ION2 Settlement Helper")
st.caption("수수료 시스템 완벽 보정 (판매자 22% / 팀원 12%)")

col_left, col_right = st.columns([1, 1.2], gap="large")

with col_left:
    st.subheader("📋 입력 정보")
    
    k = st.number_input("총 참여 인원", min_value=1, value=6, step=1)
    a = st.number_input("기타 공제액 (원)", value=0, step=1000)
    
    st.write("---")
    st.write("#### 💰 판매 아이템 리스트")
    
    # 아이템 입력창 생성
    updated_items = []
    for i, item in enumerate(st.session_state.items):
        item_col, btn_col = st.columns([4, 1])
        with item_col:
            # key를 id로 설정하여 인덱스가 변해도 에러가 안 나게 함
            new_val = st.number_input(f"아이템 {i+1} 가격 (만 단위)", value=item['value'], key=f"input_{item['id']}")
            updated_items.append({'id': item['id'], 'value': new_val})
        with btn_col:
            st.write("") # 수직 정렬용
            st.write("")
            if st.button("🗑️", key=f"del_{item['id']}"):
                remove_item(i)
    
    # 변경된 값 세션에 저장
    st.session_state.items = updated_items

    st.button("➕ 아이템 추가", on_click=add_item, use_container_width=True)

# --- 4. 계산 로직 ---
total_sales = sum(item['value'] for item in st.session_state.items) * 10000
pure_profit = total_sales * 0.78
listing_price = (pure_profit / (k - 0.12)) - a
real_share = listing_price * 0.88

# --- 5. 결과 화면 ---
with col_right:
    st.subheader("📊 정산 결과 요약")
    
    res_c1, res_c2 = st.columns(2)
    with res_c1:
        st.markdown(f"""<div class="result-card">
            <p style="color:#888; font-size:14px;">인당 최종 실수령액</p>
            <p class="gold-val">{int(real_share):,}원</p>
        </div>""", unsafe_allow_html=True)
    
    with res_c2:
        st.markdown(f"""
    <div class="summary-box">
        <p style="margin-bottom:10px;"><b>아이템 합계:</b> {total_sales:,}원</p>
        <p style="margin-bottom:10px;"><b>판매자 순수 정산금:</b> {int(pure_profit):,}원</p>
        <hr>
        <div style="display:flex; justify-content:space-between; margin-bottom:5px;">
            <span>나머지 팀원 ({k-1}명) 총 이체액</span>
            <span>{int(listing_price * (k-1)):,}원</span>
        </div>
        <div style="display:flex; justify-content:space-between;">
            <span style="color:#FFB800; font-weight:bold;">판매자 본인 몫 (잔액)</span>
            <span style="color:#FFB800; font-weight:bold;">{int(pure_profit - (listing_price * (k-1))):,}원</span>
        </div>
    </div>
    """, unsafe_allow_html=True)