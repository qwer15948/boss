import streamlit as st
import re
from supabase import create_client, Client

# ==========================================
# 1. 페이지 설정 및 DB 연결
# ==========================================
st.set_page_config(page_title="아이온2 정산기", page_icon="🎲", layout="wide")

# Streamlit Cloud의 Secrets에 저장된 정보를 가져옵니다.
# 로컬 테스트 시에는 .streamlit/secrets.toml 파일에 작성하세요.
try:
    url: str = st.secrets["SUPABASE_URL"]
    key: str = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
except Exception:
    st.error("DB 연결 설정(Secrets)이 필요합니다.")

# --- DB 연동 함수 ---
def get_db_memo():
    """DB에서 ID 1번 메모를 가져옴"""
    try:
        res = supabase.table("memos").select("content").eq("id", 1).execute()
        return res.data[0]['content'] if res.data else "기록된 메모가 없습니다."
    except:
        return "데이터를 불러오는 중 오류가 발생했습니다."

def update_db_memo(new_text):
    """DB의 ID 1번 메모를 업데이트"""
    try:
        supabase.table("memos").update({"content": new_text}).eq("id", 1).execute()
        return True
    except:
        return False

# ==========================================
# 2. 세션 및 데이터 초기화
# ==========================================
if 'init' not in st.session_state:
    st.session_state.init = True
    st.session_state['ni_0'] = '필보'
    st.session_state['pi_0'] = '7,500,000'

# ==========================================
# 3. 커스텀 CSS (디자인)
# ==========================================
st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"] { background-color: #0E1117 !important; color: #fafafa !important; }
    .block-container { max-width: 1000px; padding-top: 2rem; }

    /* 정산기 아이템 카드 */
    [data-testid="stVerticalBlock"] > div:has(div.item-card-marker) {
        background-color: #262626 !important;
        padding: 20px !important;
        border-radius: 12px !important;
        border: 1px solid #333 !important;
        margin-bottom: 15px !important;
    }

    /* 사이드바 및 메모장 */
    [data-testid="stSidebar"] { background-color: #161a21 !important; min-width: 350px !important; }
    .memo-display {
        background-color: #1E1E1E; padding: 18px; border-radius: 8px;
        border: 1px dashed #FFB800; color: #ddd; white-space: pre-wrap;
        margin-bottom: 20px; min-height: 150px; font-size: 14px; line-height: 1.6;
    }

    .label-box { color: #AAA; font-size: 14px; font-weight: bold; display: flex; align-items: center; height: 42px; }
    .item-badge { background-color: #FFB800; color: #000; border-radius: 50%; width: 22px; height: 22px; 
                  display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 11px; margin-top: 10px; }
    
    div[data-testid="stTextInput"] label { display: none !important; }
    input { background-color: #1E1E1E !important; border: 1px solid #444 !important; border-radius: 8px !important; color: white !important; }

    /* 삭제 버튼(X) */
    div.stButton > button[key^="del_"] {
        height: 42px !important; width: 42px !important; min-width: 42px !important;
        background-color: #333 !important; color: #888 !important; border-radius: 8px !important;
    }
    
    /* 결과 카드 */
    .result-card { background-color: #1E1E1E; padding: 25px; border-radius: 12px; border: 1px solid #333; text-align: center; margin-bottom: 15px; }
    .gold-val { color: #FFB800; font-weight: bold; font-size: 22px !important; }
    .white-val { color: #FFFFFF; font-weight: bold; font-size: 22px !important; }
    .summary-box { background-color: #161616; padding: 20px; border-radius: 10px; border-left: 4px solid #FFB800; margin: 20px 0px;}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 4. 사이드바 (실시간 공유 메모장)
# ==========================================
with st.sidebar:
    st.title("📝 팀 공용 메모장")
    st.caption("모든 접속자가 실시간으로 공유하는 메모입니다.")
    
    # DB에서 최신 메모 읽기
    current_memo = get_db_memo()
    st.markdown(f'<div class="memo-display">{current_memo}</div>', unsafe_allow_html=True)
    
    st.write("---")
    # 관리자 암호 확인
    pwd = st.text_input("🔑 관리자 암호", type="password", placeholder="수정하려면 0101 입력")
    
    if pwd == "0101":
        new_content = st.text_area("내용 수정하기", value=current_memo, height=300)
        if st.button("💾 모든 팀원에게 실시간 반영", use_container_width=True):
            if update_db_memo(new_content):
                st.success("DB 저장 완료!")
                st.rerun()
            else:
                st.error("저장 실패. DB 설정을 확인하세요.")

# ==========================================
# 5. 정산기 기능 함수
# ==========================================
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

# ==========================================
# 6. 메인 화면 (정산기 본체)
# ==========================================
st.title("🎲 아이온2 필보 정산기")
st.info("💡 오른쪽 메모장은 비밀번호(0101)를 아는 사람만 수정할 수 있습니다.")

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
        
        with st.container():
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

# --- 계산 로직 ---
total_sales = 0
for key in st.session_state.keys():
    if key.startswith('pi_'):
        val = re.sub(r'[^0-9]', '', st.session_state[key])
        total_sales += int(val) if val else 0

pure_profit = total_sales * 0.78 - a
listing_price = (pure_profit / (k - 0.12)) 
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
        <div style="display:flex; justify-content:space-between; margin-bottom:10px;"><span style="color:#888;">💰 순수 정산금 (0.78T)</span><span>{int(pure_profit):,}원</span></div>
        <hr style="border:0.1px solid #333; margin:15px 0;">
        <div style="display:flex; justify-content:space-between; margin-bottom:10px;"><span style="color:#AAA;">팀원 {k-1}명 총 이체액</span><span>{max(0, int(listing_price * (k-1))):,}원</span></div>
        <div style="display:flex; justify-content:space-between;"><span style="color:#888;">판매자 본인 몫 (잔액)</span><b style="color:#FFB800;">{max(0, int(pure_profit - (listing_price * (k-1)))):,}원</b></div>
    </div>
    """, unsafe_allow_html=True)
    
    copy_text = f"💎 아이온2 필보 정산 결과\n- 거래소 등록가: {max(0, int(listing_price)):,} 키나\n- 인당 실수령액: {max(0, int(real_share)):,} 키나"
    st.code(copy_text, language=None)