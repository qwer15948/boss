import streamlit as st
import re
from supabase import create_client, Client
from datetime import datetime

# ==========================================
# 1. 페이지 설정 및 DB 연결
# ==========================================
st.set_page_config(page_title="아이온2 정산기", page_icon="🎲", layout="wide")

try:
    url: str = st.secrets["SUPABASE_URL"]
    key: str = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
except:
    st.error("DB 연결 설정(Secrets)이 필요합니다.")

# --- DB 연동 함수 ---
def get_db_memo():
    res = supabase.table("memos").select("content").eq("id", 1).execute()
    return res.data[0]['content'] if res.data else ""

def update_db_memo(new_text):
    supabase.table("memos").update({"content": new_text}).eq("id", 1).execute()

def save_to_history(boss_names, profit):
    """정산 내역 저장"""
    supabase.table("history").insert({"boss_names": boss_names, "profit": profit}).execute()

def get_total_profit():
    """누적 정산액 합계"""
    res = supabase.table("history").select("profit").execute()
    return sum(row['profit'] for row in res.data) if res.data else 0

def get_history_list():
    """최근 내역 10개"""
    res = supabase.table("history").select("*").order("created_at", desc=True).limit(10).execute()
    return res.data

# ==========================================
# 2. 커스텀 CSS (완전한 반응형 + 최대 너비 제한)
# ==========================================
st.markdown("""
    <style>
    /* 배경 및 기본 폰트 */
    html, body, [data-testid="stAppViewContainer"] { background-color: #0E1117 !important; color: #fafafa !important; }
    
    /* [핵심] PC에서 1000px 중앙 정렬, 모바일에서 가변 */
    .block-container { 
        max-width: 1000px !important; 
        padding-top: 2rem !important; 
        margin: 0 auto !important; 
    }

    /* 아이템 카드 디자인 */
    [data-testid="stVerticalBlock"] > div:has(div.item-card-marker) {
        background-color: #262626 !important; padding: 20px !important; 
        border-radius: 12px !important; border: 1px solid #333 !important; 
        margin-bottom: 15px !important; box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }

    /* 누적 정산액 배너 */
    .total-banner { 
        background: linear-gradient(90deg, #FFB800, #FF8A00); color: black; 
        padding: 20px; border-radius: 12px; text-align: center; 
        margin-bottom: 25px; font-weight: bold; font-size: 18px;
    }

    /* 모바일 대응 (768px 이하) */
    @media (max-width: 768px) {
        .block-container { max-width: 100% !important; padding-left: 1rem !important; padding-right: 1rem !important; }
        .gold-val, .white-val { font-size: 18px !important; }
        .result-card { padding: 15px !important; }
        h1 { font-size: 22px !important; }
        .total-banner { font-size: 14px; padding: 15px; }
    }

    /* 결과 카드 및 박스 */
    .result-card { background-color: #1E1E1E; padding: 25px; border-radius: 12px; border: 1px solid #333; text-align: center; margin-bottom: 12px; }
    .gold-val { color: #FFB800; font-weight: bold; font-size: 24px; }
    .white-val { color: #FFFFFF; font-weight: bold; font-size: 24px; }
    .summary-box { background-color: #161616; padding: 20px; border-radius: 10px; border-left: 4px solid #FFB800; margin: 20px 0px; font-size: 14px; }
    
    /* 기타 요소 */
    .item-badge { background-color: #FFB800; color: #000; border-radius: 50%; width: 22px; height: 22px; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 11px; margin-top: 10px; }
    div[data-testid="stTextInput"] label { display: none !important; }
    input { background-color: #1E1E1E !important; border: 1px solid #444 !important; border-radius: 8px !important; color: white !important; }
    .history-item { font-size: 12px; color: #aaa; border-bottom: 1px solid #333; padding: 10px 0; line-height: 1.4; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. 사이드바 (메모장 & 히스토리 리스트)
# ==========================================
with st.sidebar:
    st.title("📝 팀 공용 메모장")
    current_memo = get_db_memo()
    st.markdown(f'<div style="background:#1E1E1E; padding:15px; border-radius:8px; border:1px dashed #FFB800; font-size:13px; white-space:pre-wrap; margin-bottom:20px;">{current_memo}</div>', unsafe_allow_html=True)
    
    pwd = st.text_input("🔑 암호", type="password", placeholder="0101 입력 시 수정 가능")
    if pwd == "0101":
        new_content = st.text_area("내용 수정", value=current_memo, height=200)
        if st.button("💾 메모 저장", use_container_width=True):
            update_db_memo(new_content)
            st.rerun()

    st.write("---")
    st.subheader("📜 최근 정산 히스토리")
    try:
        h_list = get_history_list()
        for h in h_list:
            date_str = datetime.fromisoformat(h['created_at']).strftime('%m/%d %H:%M')
            st.markdown(f'<div class="history-item"><b>{date_str}</b><br>{h["boss_names"]}<br><span style="color:#FFB800;">인당 {h["profit"]:,}원</span></div>', unsafe_allow_html=True)
    except:
        st.info("히스토리 테이블을 확인해주세요.")

# ==========================================
# 4. 메인 화면 (정산기 본체)
# ==========================================
# 상단 누적 금액 배너
total_accumulated = get_total_profit()
st.markdown(f'<div class="total-banner">💰 지금까지 총 <span style="font-size:26px;">{total_accumulated:,}</span> 원을 벌었어요!</div>', unsafe_allow_html=True)

st.title("🎲 아이온2 정산기")

col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    st.subheader("⚙️ 설정 및 아이템")
    in_c1, in_c2 = st.columns(2)
    with in_c1: k = st.number_input("👥 참여 인원", min_value=1, value=6)
    with in_c2: a = st.number_input("💰 기타 공제액", value=0, step=10000)

    st.write("---")
    # 세션 기반 아이템 관리
    item_indices = sorted([int(key.split('_')[1]) for key in st.session_state.keys() if key.startswith('ni_')])
    if not item_indices: # 아이템이 하나도 없을 때 초기화
        st.session_state['ni_0'] = '필보'; st.session_state['pi_0'] = '0'; st.rerun()

    current_bosses = []
    for idx, i in enumerate(item_indices):
        if f'ni_{i}' not in st.session_state: continue
        current_bosses.append(st.session_state[f'ni_{i}'])
        with st.container():
            st.markdown('<div class="item-card-marker"></div>', unsafe_allow_html=True)
            r1_c1, r1_c2, r1_c3 = st.columns([1, 7.5, 1.5])
            with r1_c1: st.markdown(f'<div class="item-badge">{idx+1}</div>', unsafe_allow_html=True)
            with r1_c2: st.text_input("보스명", key=f"ni_{i}")
            with r1_c3:
                if st.button("✕", key=f"del_{i}"):
                    del st.session_state[f'ni_{i}']; del st.session_state[f'pi_{i}']; st.rerun()
            
            r2_c1, r2_c2, r2_c3 = st.columns([2, 7, 1])
            with r2_c1: st.markdown('<div style="color:#AAA; font-size:14px; margin-top:10px;">판매가</div>', unsafe_allow_html=True)
            with r2_c2:
                def price_fmt(idx=i):
                    v = re.sub(r'[^0-9]', '', st.session_state[f"pi_{idx}"])
                    st.session_state[f"pi_{idx}"] = f"{int(v):,}" if v else "0"
                st.text_input("가격", key=f"pi_{i}", on_change=price_fmt)
            with r2_c3: st.markdown('<div style="color:#AAA; font-size:14px; margin-top:10px;">원</div>', unsafe_allow_html=True)

    if st.button("＋ 아이템 추가", use_container_width=True):
        new_idx = max(item_indices) + 1 if item_indices else 0
        st.session_state[f'ni_{new_idx}'] = '필보'; st.session_state[f'pi_{new_idx}'] = '0'; st.rerun()

# --- 계산 로직 ---
total_sales = sum(int(re.sub(r'[^0-9]', '', st.session_state[k])) for k in st.session_state.keys() if k.startswith('pi_'))
pure_profit = total_sales * 0.78 - a
listing_price = (pure_profit / (k - 0.12)) if (k - 0.12) != 0 else 0
real_share = listing_price * 0.88 

with col_right:
    st.subheader("📊 정산 결과")
    res_c1, res_c2 = st.columns(2)
    with res_c1: st.markdown(f'<div class="result-card"><p style="color:#888; font-size:12px;">인당 최종 실수령액</p><p class="gold-val">{max(0, int(real_share)):,}원</p></div>', unsafe_allow_html=True)
    with res_c2: st.markdown(f'<div class="result-card"><p style="color:#888; font-size:12px;">팀원 거래소 등록가</p><p class="white-val">{max(0, int(listing_price)):,}원</p></div>', unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="summary-box">
        <div style="display:flex; justify-content:space-between; margin-bottom:10px;"><span style="color:#888;">📦 총 판매액 합계</span><b>{total_sales:,}원</b></div>
        <div style="display:flex; justify-content:space-between; margin-bottom:10px;"><span style="color:#888;">💰 순수 정산금 (0.78T)</span><span>{int(pure_profit):,}원</span></div>
        <hr style="border:0.1px solid #333; margin:15px 0;">
        <div style="display:flex; justify-content:space-between;"><span style="color:#888;">판매자 본인 몫 (잔액)</span><b style="color:#FFB800;">{max(0, int(pure_profit - (listing_price * (k-1)))):,}원</b></div>
    </div>
    """, unsafe_allow_html=True)
    
    st.write("---")
    if st.button("✅ 이 정산 내역 확정 및 DB 저장", use_container_width=True, type="primary"):
        boss_names_str = ", ".join(current_bosses)
        save_to_history(boss_names_str, int(real_share))
        st.success("성공적으로 저장되었습니다!")
        st.rerun()

    st.code(f"💎 등록가: {max(0, int(listing_price)):,} / 실수령: {max(0, int(real_share)):,}", language=None)