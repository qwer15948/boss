import streamlit as st
import re

# 1. 페이지 설정
st.set_page_config(page_title="아이온2 정산기", page_icon="🎲", layout="wide")

# 2. 세션 초기화 (방어 코드 포함)
if 'item_data' not in st.session_state:
    st.session_state.item_data = [{'name': '필보', 'price_str': '7,500,000'}]

# --- 3. 커스텀 CSS (카드 내부 여백 및 테두리 완벽 고정) ---
st.markdown("""
    <style>
    .block-container { max-width: 950px; padding-top: 2rem; }
    .main { background-color: #0E1117; }
    
    /* [핵심] 카드 컨테이너: 위젯을 감싸는 실제 div 스타일 */
    [data-testid="stVerticalBlock"] > div:has(div.item-card-marker) {
        background-color: #262626;
        padding: 20px !important;
        border-radius: 15px;
        border: 1px solid #444;
        margin-bottom: 15px;
    }
    
    /* 레이블 및 텍스트 스타일 */
    .label-row { color: #AAA; font-size: 13px; font-weight: bold; margin-top: 10px; }
    .item-badge {
        background-color: #FFB800; color: #000; border-radius: 50%;
        width: 24px; height: 24px; display: flex; align-items: center;
        justify-content: center; font-weight: bold; font-size: 13px;
    }

    /* 입력창 디자인 */
    div[data-testid="stTextInput"] label { display: none; }
    input {
        background-color: #1E1E1E !important;
        border: 1px solid #444 !important;
        border-radius: 8px !important;
        color: white !important;
    }
    
    /* 삭제 버튼 */
    .stButton > button {
        height: 42px; width: 42px; background-color: #333;
        border: 1px solid #444; color: #888; border-radius: 8px;
    }
    
    /* 결과창 디자인 */
    .result-card { background-color: #1E1E1E; padding: 25px; border-radius: 12px; border: 1px solid #333; text-align: center; margin-bottom: 15px; }
    .summary-box { background-color: #161616; padding: 20px; border-radius: 10px; border-left: 4px solid #FFB800; }
    .gold-val { color: #FFB800; font-weight: bold; font-size: 28px; }
    .white-val { color: #FFFFFF; font-weight: bold; font-size: 28px; }
    hr { border: 0.1px solid #333; margin: 15px 0; }
    </style>
    """, unsafe_allow_html=True)

# --- 유틸리티 함수 (콤마) ---
def format_comma(val):
    num = re.sub(r'[^0-9]', '', str(val))
    if not num: return "0"
    return f"{int(num):,}"

# --- 콜백 함수 (실시간 업데이트용) ---
def update_item(idx, key_type):
    # 입력한 즉시 세션 데이터를 콤마 처리된 상태로 업데이트
    if key_type == 'price':
        raw_val = st.session_state[f"pi_{idx}"]
        st.session_state.item_data[idx]['price_str'] = format_comma(raw_val)
    elif key_type == 'name':
        st.session_state.item_data[idx]['name'] = st.session_state[f"ni_{idx}"]

def add_item():
    st.session_state.item_data.append({'name': '필보', 'price_str': '0'})

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
        k = st.number_input("👥 참여 인원", min_value=1, value=6, step=1)
    with in_c2:
        a = st.number_input("💰 기타 공제액", value=0, step=10000, format="%d")

    st.write("---")
    st.write("#### 📦 판매 아이템 리스트")
    
    # 아이템 리스트 렌더링
    for i, item in enumerate(st.session_state.item_data):
        # [카드 컨테이너 시작]
        with st.container():
            # CSS 선택자를 위한 마커
            st.markdown('<div class="item-card-marker"></div>', unsafe_allow_html=True)
            
            # 1층: 번호 + 이름 + 삭제
            h_c1, h_c2, h_c3 = st.columns([0.8, 8, 1.2])
            with h_c1:
                st.markdown(f'<div style="margin-top:10px;" class="item-badge">{i+1}</div>', unsafe_allow_html=True)
            with h_c2:
                st.text_input("보스명", value=item['name'], key=f"ni_{i}", on_change=update_item, args=(i, 'name'))
            with h_c3:
                if st.button("✕", key=f"db_{i}"):
                    remove_item(i)
            
            # 2층: 라벨 + 가격 + 단위
            p_c1, p_c2, p_c3 = st.columns([1.5, 7.5, 1])
            with p_c1:
                st.markdown('<div class="label-row">판매가</div>', unsafe_allow_html=True)
            with p_c2:
                # [실시간 콤마의 핵심] on_change 콜백 사용
                st.text_input("가격", value=item['price_str'], key=f"pi_{i}", on_change=update_item, args=(i, 'price'))
            with p_c3:
                st.markdown('<div class="label-row">원</div>', unsafe_allow_html=True)
            
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
        st.markdown(f'<div class="result-card"><p style="color:#888; font-size:13px;">인당 최종 실수령액</p><p class="gold-val">{max(0, int(real_share)):,}원</p></div>', unsafe_allow_html=True)
    with res_c2:
        st.markdown(f'<div class="result-card"><p style="color:#888; font-size:13px;">팀원 거래소 등록가</p><p class="white-val">{max(0, int(listing_price)):,}원</p></div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="summary-box">
        <div style="display:flex; justify-content:space-between; margin-bottom:10px;"><span style="color:#888;">📦 총 판매액 합계</span><b>{total_sales:,}원</b></div>
        <div style="display:flex; justify-content:space-between; margin-bottom:10px;"><span style="color:#888;">💰 판매자 순수 정산금 (0.78T)</span><span>{int(pure_profit):,}원</span></div>
        <hr style="border:0.1px solid #333; margin:15px 0;">
        <div style="display:flex; justify-content:space-between; margin-bottom:10px;"><span style="color:#AAA;">팀원 {k-1}명 총 이체액</span><span>{max(0, int(listing_price * (k-1))):,}원</span></div>
        <div style="display:flex; justify-content:space-between;"><span style="color:#FFB800; font-weight:bold;">판매자 본인 몫 (잔액)</span><b style="color:#FFB800;">{max(0, int(pure_profit - (listing_price * (k-1)))):,}원</b></div>
    </div>
    """, unsafe_allow_html=True)