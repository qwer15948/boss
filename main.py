import streamlit as st
import re

# 1. 페이지 설정
st.set_page_config(page_title="아이온2 정산기", page_icon="🎲", layout="wide")

# 2. 세션 초기화 (원본 유지)
if 'item_count' not in st.session_state:
    st.session_state.item_count = 1
    st.session_state['ni_0'] = '필보'
    st.session_state['pi_0'] = '7,500,000'

# --- 3. 커스텀 CSS (min-width 추가 및 X버튼 정렬) ---
st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #0E1117 !important;
        color: #fafafa !important;
    }
    .block-container { max-width: 950px; padding-top: 2rem; }
    
    div[data-testid="stVerticalBlockBorderWrapper"]:has(.item-card-marker) {
        background-color: #262626 !important;
        padding: 20px !important;
        border-radius: 12px !important;
        border: 1px solid #333 !important;
        margin-bottom: 15px !important;
    }

    .label-box { color: #AAA; font-size: 14px; font-weight: bold; display: flex; align-items: center; height: 42px; }
    .item-badge {
        background-color: #FFB800; color: #000; border-radius: 50%;
        width: 22px; height: 22px; display: flex; align-items: center;
        justify-content: center; font-weight: bold; font-size: 11px;
        margin-top: 10px;
    }

    div[data-testid="stTextInput"] label { display: none !important; }
    input { background-color: #1E1E1E !important; border: 1px solid #444 !important; border-radius: 8px !important; color: white !important; }

    /* X 버튼 보정: min-width 추가 및 찌그러짐 방지 */
    div.stButton > button[key^="del_"] {
        height: 42px !important;
        width: 42px !important;
        min-width: 42px !important; /* 요청하신 최소 너비 고정 */
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        padding: 0 !important;
        background-color: #333 !important;
        border: 1px solid #444 !important;
        color: #888 !important;
        font-size: 20px !important;
        line-height: 1 !important;
        border-radius: 8px !important;
    }

    div.stButton > button[key="add_btn"] {
        background-color: #333 !important; color: #FFB800 !important;
        border: 1px solid #FFB800 !important; height: 50px !important;
        font-weight: bold !important; border-radius: 10px !important;
    }
    
    /* 복사 버튼 스타일 */
    div.stButton > button[key="copy_btn"] {
        background-color: #FFB800 !important;
        color: #000 !important;
        font-weight: bold !important;
        border: none !important;
        width: 100% !important;
        margin-top: 10px !important;
    }

    .result-card { background-color: #1E1E1E; padding: 25px; border-radius: 12px; border: 1px solid #333; text-align: center; margin-bottom: 15px; }
    .gold-val, .white-val { font-weight: bold; font-size: 20px !important; }
    .gold-val { color: #FFB800; }
    .white-val { color: #FFFFFF; }
    .summary-box { background-color: #161616; padding: 20px; border-radius: 10px; border-left: 4px solid #FFB800; margin: 20px 0px;}
    hr { border: 0.1px solid #333; margin: 20px ; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. 기능 함수 ---
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

# --- 5. 메인 화면 ---
st.title("🎲 아이온2 필보 정산기")
st.caption("거래소 수수료 20% | 등록 수수료 2% | 개인 판매 수수료 10%")

col_left, col_right = st.columns([1, 1], gap="large")

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
                    del st.session_state[f'ni_{i}']
                    del st.session_state[f'pi_{i}']
                    st.rerun()
            
            r2_c1, r2_c2, r2_c3 = st.columns([1.8, 7.2, 1])
            with r2_c1:
                st.markdown('<div class="label-box">판매가</div>', unsafe_allow_html=True)
            with r2_c2:
                st.text_input("가격", key=f"pi_{i}", on_change=on_price_change, args=(i,))
            with r2_c3:
                st.markdown('<div class="label-box">원</div>', unsafe_allow_html=True)
            display_num += 1

    st.button("＋ 아이템 추가", key="add_btn", on_click=add_item, use_container_width=True)

# --- 6. 계산 로직 ---
total_sales = 0
current_pi_keys = [k for k in st.session_state.keys() if k.startswith('pi_')]
for pk in current_pi_keys:
    val = re.sub(r'[^0-9]', '', st.session_state[pk])
    total_sales += int(val) if val else 0

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
    
    st.markdown(f"""
    <div class="summary-box">
        <div style="display:flex; justify-content:space-between; margin-bottom:10px;"><span style="color:#888;">📦 총 판매액 합계</span><b>{total_sales:,}원</b></div>
        <div style="display:flex; justify-content:space-between; margin-bottom:10px;"><span style="color:#888;">💰 판매자 순수 정산금 (0.78T)</span><span>{int(pure_profit):,}원</span></div>
        <hr style="border:0.1px solid #333; margin:15px 0;">
        <div style="display:flex; justify-content:space-between; margin-bottom:10px;"><span style="color:#AAA;">팀원 {k-1}명 총 이체액</span><span>{max(0, int(listing_price * (k-1))):,}원</span></div>
        <div style="display:flex; justify-content:space-between;"><span style="color:#888;">판매자 본인 몫 (잔액)</span><b style="color:#FFB800;">{max(0, int(pure_profit - (listing_price * (k-1)))):,}원</b></div>
    </div>
    """, unsafe_allow_html=True)

    
    # --- 결과 복사 기능 ---
    copy_text = f"💎 아이온2 필보 정산 결과\n- 거래소 등록가: {max(0, int(listing_price)):,} 키나\n- 인당 실수령액: {max(0, int(real_share)):,} 키나"
    
    # st.text_area를 활용한 간편 복사 UI
    st.code(copy_text, language=None)


# --- 1. 파티별 이동 순서 데이터 ---
# 유저님이 주신 순서 그대로 리스트화했습니다.
party_routes = {
    1: ["가르투아", "카샤파", "타르탄", "바르시엔", "악시오스", "노블루드", "비슈베다"],
    2: ["구루타", "쉬라크", "카샤파", "타르탄", "카루카", "악시오스", "노블루드", "비슈베다"],
    3: ["가르투아", "카샤파", "타르탄", "카루카", "악시오스", "비슈베다"],
    4: ["쉬라크", "카샤파", "타르탄", "카루카", "악시오스", "노블루드", "비슈베다"]
}

# 보스별 주기(배경색 결정용)
# 주시는 정보에 따라 4h, 6h, 12h를 임의 할당했습니다. 필요시 수정하세요!
boss_info = {
    "가르투아": "4h", "구루타": "4h", "쉬라크": "4h", 
    "카샤파": "6h", "타르탄": "6h", "바르시엔": "4h", "카루카": "4h",
    "악시오스": "6h", "노블루드": "12h", "비슈베다": "12h"
}

# --- 2. 스타일 설정 ---
st.set_page_config(layout="wide", page_title="필드 보스 작전판")
st.markdown("""
    <style>
    .party-header {
        text-align: center; padding: 12px;
        background-color: #1E1E1E; border-radius: 10px;
        border-bottom: 4px solid #FFB800; margin-bottom: 20px;
        font-weight: bold; font-size: 18px; color: #EEE;
    }
    .boss-card {
        padding: 15px; border-radius: 12px; margin-bottom: 15px;
        border: 1px solid transparent; position: relative;
    }
    /* 주기별 색상 */
    .cycle-4h { background-color: #262626; border-left: 5px solid #888; }
    .cycle-6h { background-color: #1A2635; border-left: 5px solid #00A3FF; }
    .cycle-12h { background-color: #332B12; border-left: 5px solid #FFB800; border: 1px solid #FFB80044; }
    
    .order-badge {
        position: absolute; top: 10px; right: 15px;
        background: rgba(255,255,255,0.1); padding: 2px 8px;
        border-radius: 20px; font-size: 12px; color: #AAA;
    }
    .boss-name { font-size: 17px; font-weight: bold; color: #FFF; margin-top: 5px; }
    .coop-tag { font-size: 11px; color: #999; margin-top: 8px; display: block; }
    </style>
    """, unsafe_allow_html=True)

st.title("⚔️ 파티별 보스 토벌 시퀀스")
st.caption("각 파티는 위에서 아래 순서대로 이동합니다. (12시간 통합 젠 기준)")

# --- 3. 레이아웃 렌더링 ---
cols = st.columns(4)
party_names = ["1파티", "2파티", "3파티", "4파티"]

for i in range(4):
    p_num = i + 1
    with cols[i]:
        st.markdown(f'<div class="party-header">{party_names[i]}</div>', unsafe_allow_html=True)
        
        # 해당 파티의 경로를 순서대로 출력
        for idx, name in enumerate(party_routes[p_num]):
            cycle = boss_info.get(name, "4h")
            
            # 다른 파티도 이 보스를 잡는지 확인 (협동 체크)
            coop_parties = [str(p) for p, route in party_routes.items() if name in route and p != p_num]
            coop_text = f"🤝 {', '.join(coop_parties)}파티 합류" if coop_parties else "👤 단독 처리"
            
            st.markdown(f"""
                <div class="boss-card cycle-{cycle}">
                    <div class="order-badge">{idx + 1}번째</div>
                    <div class="boss-name">{name}</div>
                    <span class="coop-tag">{coop_text}</span>
                </div>
            """, unsafe_allow_html=True)

st.sidebar.markdown("### 💡 범례")
st.sidebar.info("🔘 회색: 4시간 주기\n\n🔵 파랑: 6시간 주기\n\n🟡 황금: 12시간 주기")