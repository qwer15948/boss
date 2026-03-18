import streamlit as st
import re

# 1. 페이지 설정
st.set_page_config(page_title="아이온2 정산기", page_icon="🎲", layout="wide")

# 2. 데이터 및 세션 초기화
if 'item_count' not in st.session_state:
    st.session_state.item_count = 1
    st.session_state['ni_0'] = '필보'
    st.session_state['pi_0'] = '7,500,000'

# 보스 데이터 (NO 추가 및 경로 설정)
# 유저님의 순서에 맞춰 NO를 임의로 넣었습니다. 실제 번호로 수정해서 쓰세요!
boss_db = {
    "가르투아": {"no": 10, "cycle": "4h"},
    "카샤파": {"no": 15, "cycle": "6h"},
    "타르탄": {"no": 18, "cycle": "6h"},
    "바르시엔": {"no": 22, "cycle": "4h"},
    "악시오스": {"no": 30, "cycle": "6h"},
    "노블루드": {"no": 45, "cycle": "12h"},
    "비슈베다": {"no": 50, "cycle": "12h"},
    "구루타": {"no": 11, "cycle": "4h"},
    "쉬라크": {"no": 12, "cycle": "4h"},
    "카루카": {"no": 25, "cycle": "4h"},
}

party_routes = {
    1: ["가르투아", "카샤파", "타르탄", "바르시엔", "악시오스", "노블루드", "비슈베다"],
    2: ["구루타", "쉬라크", "카샤파", "타르탄", "카루카", "악시오스", "노블루드", "비슈베다"],
    3: ["가르투아", "카샤파", "타르탄", "카루카", "악시오스", "비슈베다"],
    4: ["쉬라크", "카샤파", "타르탄", "카루카", "악시오스", "노블루드", "비슈베다"]
}

# --- 3. 커스텀 CSS ---
st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #0E1117 !important;
        color: #fafafa !important;
    }
    .block-container { max-width: 1000px; padding-top: 2rem; }
    
    /* 사이드바 스타일 */
    [data-testid="stSidebar"] { background-color: #161a21 !important; min-width: 350px !important; }
    
    /* 보스 카드 공통 스타일 */
    .boss-card-static {
        padding: 12px 15px;
        border-radius: 10px;
        margin-bottom: 10px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .boss-no-text { font-size: 11px; color: rgba(255,255,255,0.5); font-weight: bold; }
    .boss-name-text { font-size: 18px; font-weight: bold; color: #FFF; margin-top: 2px; }
    
    /* 등급별 배경색 */
    .bg-4h { background-color: #262626; border-left: 5px solid #888; }
    .bg-6h { background-color: #1A2635; border-left: 5px solid #00A3FF; }
    .bg-12h { background-color: #332B12; border-left: 5px solid #FFB800; border: 1px solid rgba(255,184,0,0.2); }

    /* 정산기 카드 스타일 */
    div[data-testid="stVerticalBlockBorderWrapper"]:has(.item-card-marker) {
        background-color: #262626 !important;
        padding: 20px !important;
        border-radius: 12px !important;
        border: 1px solid #333 !important;
        margin-bottom: 15px !important;
    }
    .item-badge {
        background-color: #FFB800; color: #000; border-radius: 50%;
        width: 22px; height: 22px; display: flex; align-items: center;
        justify-content: center; font-weight: bold; font-size: 11px;
    }
    .result-card { background-color: #1E1E1E; padding: 25px; border-radius: 12px; border: 1px solid #333; text-align: center; margin-bottom: 15px; }
    .gold-val { color: #FFB800; font-weight: bold; font-size: 20px !important; }
    .white-val { color: #FFFFFF; font-weight: bold; font-size: 20px !important; }
    .summary-box { background-color: #161616; padding: 20px; border-radius: 10px; border-left: 4px solid #FFB800; margin: 20px 0px;}
    </style>
    """, unsafe_allow_html=True)

# --- 4. 사이드바 (필드보스 시퀀스 - 카드형) ---
with st.sidebar:
    st.title("⚔️ 보스 타임라인")
    tabs = st.tabs(["1파티", "2파티", "3파티", "4파티"])
    
    for i, tab in enumerate(tabs):
        p_num = i + 1
        with tab:
            st.write("") # 간격 조절
            for idx, name in enumerate(party_routes[p_num]):
                info = boss_db.get(name, {"no": 0, "cycle": "4h"})
                no_val = info['no']
                cycle = info['cycle']
                
                # 카드 출력 (HTML)
                st.markdown(f"""
                    <div class="boss-card-static bg-{cycle}">
                        <div class="boss-no-text">NO. {no_val:02d} | {idx+1}번째</div>
                        <div class="boss-name-text">{name}</div>
                    </div>
                """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("""<div style="font-size:11px; color:#666; text-align:center;">🔘 4h | 🔵 6h | 🟡 12h</div>""", unsafe_allow_html=True)

# --- 5. 기능 함수 (정산기용) ---
def format_comma(val):
    num = re.sub(r'[^0-9]', '', str(val))
    return f"{int(num):,}" if num else "0"

def on_price_change(idx):
    key = f"pi_{idx}"
    if key in st.session_state:
        st.session_state[key] = format_comma(st.session_state[key])

def add_item():
    existing_indices = [int(k.split('_')[1]) for k in st.session_state.keys() if k.startswith('ni_')]
    next_idx = max(existing_indices) + 1 if existing_indices else 0
    st.session_state[f'ni_{next_idx}'] = '필보'
    st.session_state[f'pi_{next_idx}'] = '0'

# --- 6. 메인 화면 (정산기) ---
st.title("🎲 아이온2 필보 정산기")
st.caption("거래소 수수료 20% | 등록 수수료 2% | 개인 판매 수수료 10%")

col_left, col_right = st.columns([1.1, 0.9], gap="large")

with col_left:
    in_c1, in_c2 = st.columns(2)
    with in_c1:
        k = st.number_input("👥 참여 인원", min_value=1, value=6, step=1)
    with in_c2:
        a = st.number_input("💰 기타 공제액", value=0, step=10000, format="%d")

    st.write("---")
    st.write("#### 📦 판매 아이템 리스트")
    
    item_indices = sorted([int(k.split('_')[1]) for k in st.session_state.keys() if k.startswith('ni_')])
    
    display_num = 1
    for i in item_indices:
        if f'ni_{i}' not in st.session_state: continue
        with st.container(border=True):
            st.markdown('<div class="item-card-marker"></div>', unsafe_allow_html=True)
            r1_c1, r1_c2, r1_c3 = st.columns([1, 7.5, 1.5], gap="small")
            with r1_c1:
                st.markdown(f'<div class="item-badge">{display_num}</div>', unsafe_allow_html=True)
            with r1_c2:
                st.text_input("보스명", key=f"ni_{i}")
            with r1_c3:
                if st.button("✕", key=f"del_{i}"):
                    del st.session_state[f'ni_{i}']; del st.session_state[f'pi_{i}']
                    st.rerun()
            r2_c1, r2_c2, r2_c3 = st.columns([1.8, 7.2, 1])
            with r2_c1:
                st.markdown('<div style="color:#AAA; font-size:14px; font-weight:bold; display:flex; align-items:center; height:42px;">판매가</div>', unsafe_allow_html=True)
            with r2_c2:
                st.text_input("가격", key=f"pi_{i}", on_change=on_price_change, args=(i,))
            with r2_c3:
                st.markdown('<div style="color:#AAA; font-size:14px; font-weight:bold; display:flex; align-items:center; height:42px;">원</div>', unsafe_allow_html=True)
            display_num += 1
    st.button("＋ 아이템 추가", key="add_btn", on_click=add_item, use_container_width=True)

# --- 7. 계산 및 결과 출력 ---
total_sales = sum(int(re.sub(r'[^0-9]', '', st.session_state[k])) for k in st.session_state.keys() if k.startswith('pi_') and st.session_state[k])
pure_profit = total_sales * 0.78 
listing_price = (pure_profit / (k - 0.12)) - a 
real_share = listing_price * 0.88 

with col_right:
    st.subheader("📊 정산 결과")
    res_c1, res_c2 = st.columns(2)
    with res_c1:
        st.markdown(f'<div class="result-card"><p style="color:#888; font-size: 13px;">인당 최종 실수령액</p><p class="gold-val">{max(0, int(real_share)):,}원</p></div>', unsafe_allow_html=True)
    with res_c2:
        st.markdown(f'<div class="result-card"><p style="color:#888; font-size: 13px;">팀원 거래소 등록가</p><p class="white-val">{max(0, int(listing_price)):,}원</p></div>', unsafe_allow_html=True)
    st.markdown(f"""<div class="summary-box">
        <div style="display:flex; justify-content:space-between; margin-bottom:10px;"><span style="color:#888;">📦 총 판매액 합계</span><b>{total_sales:,}원</b></div>
        <div style="display:flex; justify-content:space-between; margin-bottom:10px;"><span style="color:#888;">💰 판매자 순수 정산금 (0.78T)</span><span>{int(pure_profit):,}원</span></div>
        <hr style="border:0.1px solid #333; margin:15px 0;">
        <div style="display:flex; justify-content:space-between; margin-bottom:10px;"><span style="color:#AAA;">팀원 {k-1}명 총 이체액</span><span>{max(0, int(listing_price * (k-1))):,}원</span></div>
        <div style="display:flex; justify-content:space-between;"><span style="color:#888;">판매자 본인 몫 (잔액)</span><b style="color:#FFB800;">{max(0, int(pure_profit - (listing_price * (k-1)))):,}원</b></div>
    </div>""", unsafe_allow_html=True)
    st.code(f"💎 아이온2 필보 정산 결과\n- 등록가: {max(0, int(listing_price)):,} 키나\n- 실수령: {max(0, int(real_share)):,} 키나", language=None)