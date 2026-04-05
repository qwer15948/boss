import streamlit as st
import re
from supabase import create_client, Client

# 1. 페이지 설정
st.set_page_config(page_title="아이온2 정산기", page_icon="🎲", layout="wide")

# (DB 연결 설정 부분 - 기존과 동일하게 유지)
try:
    url: str = st.secrets["SUPABASE_URL"]
    key: str = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
except:
    st.error("DB 연결 설정이 필요합니다.")

def get_db_memo():
    try:
        res = supabase.table("memos").select("content").eq("id", 1).execute()
        return res.data[0]['content'] if res.data else "기록된 메모가 없습니다."
    except: return "접속 오류"

def update_db_memo(new_text):
    try:
        supabase.table("memos").update({"content": new_text}).eq("id", 1).execute()
        return True
    except: return False

# 2. 세션 초기화
if 'ni_0' not in st.session_state:
    st.session_state['ni_0'] = '필보'
    st.session_state['pi_0'] = '7,500,000'

# ==========================================
# 3. [업데이트] 반응형 커스텀 CSS
# ==========================================
st.markdown("""
    <style>
    /* 1. 배경 및 기본 폰트 설정 */
    html, body, [data-testid="stAppViewContainer"] { 
        background-color: #0E1117 !important; 
        color: #fafafa !important; 
    }

    /* 2. 메인 컨테이너 최대 너비 제한 및 중앙 정렬 */
    .block-container { 
        max-width: 1000px !important; /* PC에서 눈에 제일 잘 들어오는 너비 */
        padding-left: 1.5rem !important; 
        padding-right: 1.5rem !important; 
        padding-top: 2rem !important;
        margin: 0 auto !important; /* 중앙 정렬 */
    }

    /* 3. 아이템 카드 디자인 */
    [data-testid="stVerticalBlock"] > div:has(div.item-card-marker) {
        background-color: #262626 !important;
        padding: 20px !important;
        border-radius: 12px !important;
        border: 1px solid #333 !important;
        margin-bottom: 15px !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }

    /* 4. 모바일 환경(768px 이하) 대응 */
    @media (max-width: 768px) {
        .block-container { 
            max-width: 100% !important; /* 모바일은 꽉 차게 */
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
        .gold-val, .white-val { font-size: 18px !important; }
        .result-card { padding: 15px !important; }
        h1 { font-size: 22px !important; }
    }

    /* 사이드바 메모장 디자인 */
    [data-testid="stSidebar"] { background-color: #161a21 !important; }
    .memo-display {
        background-color: #1E1E1E; padding: 15px; border-radius: 8px;
        border: 1px dashed #FFB800; color: #ddd; white-space: pre-wrap;
        margin-bottom: 20px; font-size: 13px; line-height: 1.6;
    }

    /* 공통 요소 (배지, 입력창 등) */
    .item-badge { 
        background-color: #FFB800; color: #000; border-radius: 50%; 
        width: 22px; height: 22px; display: flex; align-items: center; 
        justify-content: center; font-weight: bold; font-size: 11px; margin-top: 10px; 
    }
    div[data-testid="stTextInput"] label { display: none !important; }
    input { 
        background-color: #1E1E1E !important; border: 1px solid #444 !important; 
        border-radius: 8px !important; color: white !important; 
    }
    
    /* 결과 박스 디자인 */
    .result-card { 
        background-color: #1E1E1E; padding: 25px; border-radius: 12px; 
        border: 1px solid #333; text-align: center; margin-bottom: 12px; 
    }
    .gold-val { color: #FFB800; font-weight: bold; font-size: 24px; }
    .white-val { color: #FFFFFF; font-weight: bold; font-size: 24px; }
    .summary-box { 
        background-color: #161616; padding: 20px; border-radius: 10px; 
        border-left: 4px solid #FFB800; margin: 20px 0px; font-size: 14px;
    }
</style>
    """, unsafe_allow_html=True)

# 4. 사이드바 (메모장)
with st.sidebar:
    st.title("📝 팀 공용 메모장")
    current_memo = get_db_memo()
    st.markdown(f'<div class="memo-display">{current_memo}</div>', unsafe_allow_html=True)
    pwd = st.text_input("🔑 암호", type="password", placeholder="0101 입력 시 수정")
    if pwd == "0101":
        new_content = st.text_area("내용 수정", value=current_memo, height=250)
        if st.button("💾 저장하기", use_container_width=True):
            if update_db_memo(new_content): st.rerun()

# 5. 정산기 본체
st.title("🎲 아이온2 정산기")

# 반응형을 위해 컬럼 비율 조정 (화면이 작아지면 자동으로 아래로 내려감)
col_left, col_right = st.columns([1, 1], gap="medium")

with col_left:
    st.subheader("⚙️ 설정 및 아이템")
    in_c1, in_c2 = st.columns(2)
    with in_c1: k = st.number_input("👥 참여 인원", min_value=1, value=6)
    with in_c2: a = st.number_input("💰 기타 공제액", value=0, step=10000)

    st.write("---")
    
    item_indices = sorted([int(key.split('_')[1]) for key in st.session_state.keys() if key.startswith('ni_')])
    
    for idx, i in enumerate(item_indices):
        if f'ni_{i}' not in st.session_state: continue
        with st.container():
            st.markdown('<div class="item-card-marker"></div>', unsafe_allow_html=True)
            # 모바일 배려: 보스명과 삭제버튼을 8.5:1.5 비율로 배치
            r1_c1, r1_c2, r1_c3 = st.columns([1, 7.5, 1.5], gap="small")
            with r1_c1: st.markdown(f'<div class="item-badge">{idx+1}</div>', unsafe_allow_html=True)
            with r1_c2: st.text_input("보스명", key=f"ni_{i}")
            with r1_c3:
                if st.button("✕", key=f"del_{i}"):
                    del st.session_state[f'ni_{i}']; del st.session_state[f'pi_{i}']; st.rerun()
            
            # 판매가 입력 영역
            r2_c1, r2_c2, r2_c3 = st.columns([2, 7, 1])
            with r2_c1: st.markdown('<div class="label-box">판매가</div>', unsafe_allow_html=True)
            with r2_c2: 
                # 가격 쉼표 처리 함수
                def on_change(idx=i):
                    val = re.sub(r'[^0-9]', '', st.session_state[f"pi_{idx}"])
                    st.session_state[f"pi_{idx}"] = f"{int(val):,}" if val else "0"
                st.text_input("가격", key=f"pi_{i}", on_change=on_change)
            with r2_c3: st.markdown('<div class="label-box">원</div>', unsafe_allow_html=True)

    if st.button("＋ 아이템 추가", use_container_width=True):
        new_idx = max(item_indices) + 1 if item_indices else 0
        st.session_state[f'ni_{new_idx}'] = '필보'; st.session_state[f'pi_{new_idx}'] = '0'; st.rerun()

# 계산 로직
total_sales = sum(int(re.sub(r'[^0-9]', '', st.session_state[k])) for k in st.session_state.keys() if k.startswith('pi_'))
pure_profit = total_sales * 0.78 - a
listing_price = (pure_profit / (k - 0.12)) if (k - 0.12) != 0 else 0
real_share = listing_price * 0.88 

with col_right:
    st.subheader("📊 정산 결과")
    res_c1, res_c2 = st.columns(2)
    with res_c1: st.markdown(f'<div class="result-card"><p style="color:#888; font-size: 12px;">실수령액</p><p class="gold-val">{max(0, int(real_share)):,}원</p></div>', unsafe_allow_html=True)
    with res_c2: st.markdown(f'<div class="result-card"><p style="color:#888; font-size: 12px;">등록가</p><p class="white-val">{max(0, int(listing_price)):,}원</p></div>', unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="summary-box">
        <div style="display:flex; justify-content:space-between; margin-bottom:8px;"><span style="color:#888;">총 판매액</span><b>{total_sales:,}원</b></div>
        <div style="display:flex; justify-content:space-between; margin-bottom:8px;"><span style="color:#888;">순수 정산금</span><span>{int(pure_profit):,}원</span></div>
        <hr style="border:0.1px solid #333; margin:10px 0;">
        <div style="display:flex; justify-content:space-between; margin-bottom:8px;"><span style="color:#AAA;">팀원 이체액</span><span>{max(0, int(listing_price * (k-1))):,}원</span></div>
        <div style="display:flex; justify-content:space-between;"><span style="color:#888;">본인 몫</span><b style="color:#FFB800;">{max(0, int(pure_profit - (listing_price * (k-1)))):,}원</b></div>
    </div>
    """, unsafe_allow_html=True)
    st.code(f"💎 등록가: {max(0, int(listing_price)):,} / 실수령: {max(0, int(real_share)):,}", language=None)