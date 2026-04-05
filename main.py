import streamlit as st
import re
from supabase import create_client, Client
from datetime import datetime

# 1. 페이지 설정
st.set_page_config(page_title="아이온2 정산기", page_icon="🎲", layout="wide")

# DB 연결
try:
    url: str = st.secrets["SUPABASE_URL"]
    key: str = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
except:
    st.error("DB 연결 설정이 필요합니다.")

# --- DB 연동 함수 ---
def get_db_memo():
    res = supabase.table("memos").select("content").eq("id", 1).execute()
    return res.data[0]['content'] if res.data else ""

def update_db_memo(new_text):
    supabase.table("memos").update({"content": new_text}).eq("id", 1).execute()

def save_to_history(boss_names, profit):
    """정산 내역을 history 테이블에 저장"""
    supabase.table("history").insert({"boss_names": boss_names, "profit": profit}).execute()

def get_total_profit():
    """지금까지 번 총 금액 합계 가져오기"""
    res = supabase.table("history").select("profit").execute()
    return sum(row['profit'] for row in res.data) if res.data else 0

def get_history_list():
    """최근 정산 내역 10개 가져오기"""
    res = supabase.table("history").select("*").order("created_at", desc=True).limit(10).execute()
    return res.data

# 2. 세션 초기화
if 'ni_0' not in st.session_state:
    st.session_state['ni_0'] = '필보'; st.session_state['pi_0'] = '0'

# 3. CSS (최대 너비 제한 포함)
st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"] { background-color: #0E1117 !important; color: #fafafa !important; }
    .block-container { max-width: 1000px !important; padding-top: 2rem !important; margin: 0 auto !important; }
    
    /* 카드 및 박스 디자인 */
    [data-testid="stVerticalBlock"] > div:has(div.item-card-marker) {
        background-color: #262626 !important; padding: 20px !important; border-radius: 12px !important; border: 1px solid #333 !important; margin-bottom: 10px !important;
    }
    .result-card { background-color: #1E1E1E; padding: 25px; border-radius: 12px; border: 1px solid #333; text-align: center; margin-bottom: 12px; }
    .total-banner { background: linear-gradient(90deg, #FFB800, #FF8A00); color: black; padding: 20px; border-radius: 12px; text-align: center; margin-bottom: 25px; font-weight: bold; }
    
    /* 폰트 설정 */
    .gold-val { color: #FFB800; font-weight: bold; font-size: 24px; }
    .white-val { color: #FFFFFF; font-weight: bold; font-size: 24px; }
    .history-item { font-size: 13px; color: #aaa; border-bottom: 1px solid #333; padding: 8px 0; }
    </style>
    """, unsafe_allow_html=True)

# 4. 사이드바 (메모장 & 히스토리 요약)
with st.sidebar:
    st.title("📝 메모장")
    current_memo = get_db_memo()
    st.markdown(f'<div style="background:#1E1E1E; padding:15px; border-radius:8px; border:1px dashed #FFB800; font-size:13px; white-space:pre-wrap; margin-bottom:20px;">{current_memo}</div>', unsafe_allow_html=True)
    
    pwd = st.text_input("🔑 암호", type="password")
    if pwd == "0101":
        new_content = st.text_area("내용 수정", value=current_memo, height=200)
        if st.button("💾 메모 저장", use_container_width=True):
            update_db_memo(new_content); st.rerun()

    st.write("---")
    st.subheader("📜 최근 정산 히스토리")
    h_list = get_history_list()
    for h in h_list:
        date_str = datetime.fromisoformat(h['created_at']).strftime('%m/%d %H:%M')
        st.markdown(f'<div class="history-item"><b>{date_str}</b><br>{h["boss_names"]}<br><span style="color:#FFB800;">{h["profit"]:,}원</span></div>', unsafe_allow_html=True)

# 5. 메인 화면
total_accumulated = get_total_profit()
st.markdown(f'<div class="total-banner">💰 지금까지 총 <span style="font-size:28px;">{total_accumulated:,}</span> 원을 벌었어요!</div>', unsafe_allow_html=True)

st.title("🎲 아이온2 정산기")

col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    in_c1, in_c2 = st.columns(2)
    with in_c1: k = st.number_input("👥 참여 인원", min_value=1, value=6)
    with in_c2: a = st.number_input("💰 기타 공제액", value=0)

    st.write("---")
    item_indices = sorted([int(key.split('_')[1]) for key in st.session_state.keys() if key.startswith('ni_')])
    
    current_bosses = []
    for idx, i in enumerate(item_indices):
        if f'ni_{i}' not in st.session_state: continue
        current_bosses.append(st.session_state[f'ni_{i}'])
        with st.container():
            st.markdown('<div class="item-card-marker"></div>', unsafe_allow_html=True)
            r1_c1, r1_c2, r1_c3 = st.columns([1, 7.5, 1.5])
            with r1_c1: st.markdown(f'<div style="background:#FFB800; color:black; border-radius:50%; width:22px; height:22px; text-align:center; font-size:11px; font-weight:bold; margin-top:10px;">{idx+1}</div>', unsafe_allow_html=True)
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

# 계산
total_sales = sum(int(re.sub(r'[^0-9]', '', st.session_state[k])) for k in st.session_state.keys() if k.startswith('pi_'))
pure_profit = total_sales * 0.78 - a
listing_price = (pure_profit / (k - 0.12)) if (k - 0.12) != 0 else 0
real_share = listing_price * 0.88 

with col_right:
    st.subheader("📊 정산 결과")
    res_c1, res_c2 = st.columns(2)
    with res_c1: st.markdown(f'<div class="result-card"><p style="color:#888; font-size:12px;">실수령액</p><p class="gold-val">{max(0, int(real_share)):,}원</p></div>', unsafe_allow_html=True)
    with res_c2: st.markdown(f'<div class="result-card"><p style="color:#888; font-size:12px;">등록가</p><p class="white-val">{max(0, int(listing_price)):,}원</p></div>', unsafe_allow_html=True)
    
    st.markdown(f'<div style="background:#161616; padding:15px; border-radius:10px; border-left:4px solid #FFB800; font-size:14px;">본인 몫: <b>{max(0, int(pure_profit - (listing_price * (k-1)))):,}원</b></div>', unsafe_allow_html=True)
    
    st.write("---")
    if st.button("✅ 이 정산 내역 확정 및 DB 저장", use_container_width=True, type="primary"):
        boss_names_str = ", ".join(current_bosses)
        save_to_history(boss_names_str, int(real_share))
        st.success("히스토리에 저장되었습니다!")
        st.rerun()