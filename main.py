import streamlit as st
import re

# 1. 페이지 설정
st.set_page_config(page_title="아이온2 정산기", page_icon="🎲", layout="wide")

# 2. 세션 초기화 (item_data 구조 단순화)
if 'item_count' not in st.session_state:
    st.session_state.item_count = 1
    st.session_state['ni_0'] = '필보'
    st.session_state['pi_0'] = '7,500,000'

# --- 3. 커스텀 CSS (불필요한 부분 삭제 및 최적화) ---
st.markdown("""
    <style>
    .block-container { max-width: 950px; padding-top: 2rem; }
    .main { background-color: #0E1117; }
    
    /* 카드 컨테이너 스타일 */
    .custom-card {
        background-color: #262626;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #333;
        margin-bottom: 15px;
    }
    
    /* 판매가 라벨 줄바꿈 방지 */
    .no-wrap {
        white-space: nowrap;
        color: #AAA;
        font-size: 14px;
        font-weight: bold;
        display: flex;
        align-items: center;
        height: 42px;
    }

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
    .del-btn-style > button {
        height: 42px; width: 42px; background-color: #333;
        border: 1px solid #444; color: #888; border-radius: 8px;
        margin-top: 0px !important;
    }
    
    /* 아이템 추가 버튼 깨짐 방지 */
    .add-btn-container > button {
        background-color: #333 !important;
        border: 1px solid #444 !important;
        color: white !important;
        font-weight: bold !important;
        height: 45px;
    }

    /* 결과창 */
    .result-card { background-color: #1E1E1E; padding: 25px; border-radius: 12px; border: 1px solid #333; text-align: center; margin-bottom: 15px; }
    .gold-val { color: #FFB800; font-weight: bold; font-size: 28px; }
    .white-val { color: #FFFFFF; font-weight: bold; font-size: 28px; }
    .summary-box { background-color: #161616; padding: 20px; border-radius: 10px; border-left: 4px solid #FFB800; }
    hr { border: 0.1px solid #333; margin: 15px 0; }
    </style>
    """, unsafe_allow_html=True)

# --- 유틸리티 함수 ---
def format_comma(val):
    num = re.sub(r'[^0-9]', '', str(val))
    if not num: return "0"
    return f"{int(num):,}"

def on_price_change(idx):
    # 입력된 값을 즉시 콤마 포맷으로 변환하여 세션에 다시 저장
    key = f"pi_{idx}"
    raw = st.session_state[key]
    st.session_state[key] = format_comma(raw)

def add_item():
    idx = st.session_state.item_count
    st.session_state[f'ni_{idx}'] = '필보'
    st.session_state[f'pi_{idx}'] = '0'
    st.session_state.item_count += 1

# --- 화면 구성 ---
st.title("🎲 아이온2 필보 정산기")

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
    
    for i in range(st.session_state.item_count):
        # 삭제된 아이템 건너뛰기 로직 (간단하게 구현)
        if f'ni_{i}' not in st.session_state: continue
        
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        
        # 1층: 번호 + 이름 + 삭제
        c1, c2, c3 = st.columns([0.8, 8, 1.2])
        with c1:
            st.markdown(f'<div style="margin-top:10px;" class="item-badge">{i+1}</div>', unsafe_allow_html=True)
        with c2:
            st.text_input("보스명", key=f"ni_{i}")
        with c3:
            st.markdown('<div class="del-btn-style">', unsafe_allow_html=True)
            if st.button("✕", key=f"del_{i}"):
                del st.session_state[f'ni_{i}']
                del st.session_state[f'pi_{i}']
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        
        # 2층: 판매가 + 가격 + 원 (줄바꿈 방지)
        p1, p2, p3 = st.columns([1.8, 7.2, 1])
        with p1:
            st.markdown('<div class="no-wrap">판매가</div>', unsafe_allow_html=True)
        with p2:
            # 실시간 콤마 핵심: on_change
            st.text_input("가격", key=f"pi_{i}", on_change=on_price_change, args=(i,))
        with p3:
            st.markdown('<div class="no-wrap">원</div>', unsafe_allow_html=True)
            
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="add-btn-container">', unsafe_allow_html=True)
    st.button("＋ 아이템 추가", on_click=add_item, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- 계산 로직 ---
total_sales = 0
for i in range(st.session_state.item_count):
    if f'pi_{i}' in st.session_state:
        val = re.sub(r'[^0-9]', '', st.session_state[f'pi_{i}'])
        total_sales += int(val) if val else 0

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