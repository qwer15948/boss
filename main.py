import streamlit as st
import re

# 1. 페이지 설정
st.set_page_config(page_title="아이온2 정산기", page_icon="🎲", layout="wide")

# 2. 세션 초기화 (AttributeError 방지를 위해 가장 먼저 수행)
if 'items' not in st.session_state or st.session_state.items is None:
    st.session_state.items = {0: {"name": "필보", "price": "7,500,000"}}
if 'id_ptr' not in st.session_state:
    st.session_state.id_ptr = 1

# --- 3. 커스텀 CSS (X버튼 정중앙 정렬 보정) ---
st.markdown("""
    <style>
    .block-container { max-width: 950px; padding-top: 2rem; }
    
    /* 카드 컨테이너 스타일 */
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

    /* X 버튼: 찌그러짐 방지 및 정중앙 정렬 */
    div.stButton > button[key^="del_"] {
        height: 42px !important; width: 42px !important; min-width: 42px !important;
        padding: 0 !important; display: flex !important; align-items: center !important;
        justify-content: center !important; background-color: #333 !important;
        border: 1px solid #444 !important; color: #888 !important;
        font-size: 18px !important; line-height: 1 !important; border-radius: 8px !important;
        margin-top: 0px !important;
    }
    
    div.stButton > button[key="add_btn"] {
        background-color: #333 !important; color: #FFB800 !important;
        border: 1px solid #FFB800 !important; height: 50px !important;
        font-weight: bold !important; border-radius: 10px !important;
    }
    
    .result-card { background-color: #1E1E1E; padding: 25px; border-radius: 12px; border: 1px solid #333; text-align: center; margin-bottom: 15px; }
    .gold-val { color: #FFB800; font-weight: bold; font-size: 20px; }
    .white-val { color: #FFFFFF; font-weight: bold; font-size: 20px; }
    .summary-box { background-color: #161616; padding: 20px; border-radius: 10px; border-left: 4px solid #FFB800; }
    hr { border: 0.1px solid #333; margin: 20px 0; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. 기능 함수 ---
def format_comma(val):
    num = re.sub(r'[^0-9]', '', str(val))
    return f"{int(num):,}" if num else "0"

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
    
    # [핵심] .get()을 사용하여 items가 없어도 에러가 나지 않게 함
    current_items = st.session_state.get('items', {})
    item_keys = sorted(list(current_items.keys()))
    
    for idx, k_id in enumerate(item_keys):
        # 만약 루프 도중 데이터가 사라져도 안전하게 건너뜀
        if k_id not in st.session_state.items:
            continue
            
        with st.container(border=True):
            st.markdown('<div class="item-card-marker"></div>', unsafe_allow_html=True)
            r1_c1, r1_c2, r1_c3 = st.columns([0.8, 8, 1.2])
            
            with r1_c1:
                st.markdown(f'<div class="item-badge">{idx+1}</div>', unsafe_allow_html=True)
            with r1_c2:
                # 위젯에서 직접 세션 데이터 수정
                st.session_state.items[k_id]["name"] = st.text_input(
                    f"name_{k_id}", 
                    value=st.session_state.items[k_id]["name"], 
                    key=f"nm_{k_id}"
                )
            with r1_c3:
                # 삭제 버튼 클릭 시 처리
                if st.button("✕", key=f"del_{k_id}"):
                    if k_id in st.session_state.items:
                        del st.session_state.items[k_id]
                        st.rerun()
            
            r2_c1, r2_c2, r2_c3 = st.columns([1.8, 7.2, 1])
            with r2_c1:
                st.markdown('<div class="label-box">판매가</div>', unsafe_allow_html=True)
            with r2_c2:
                p_val = st.text_input(
                    f"price_{k_id}", 
                    value=st.session_state.items[k_id]["price"], 
                    key=f"pr_{k_id}"
                )
                # 실시간 콤마 업데이트
                clean_p = re.sub(r'[^0-9]', '', p_val)
                st.session_state.items[k_id]["price"] = format_comma(clean_p)
            with r2_c3:
                st.markdown('<div class="label-box">원</div>', unsafe_allow_html=True)

    if st.button("＋ 아이템 추가", key="add_btn", use_container_width=True):
        new_ptr = st.session_state.get('id_ptr', 0)
        if 'items' not in st.session_state:
            st.session_state.items = {}
        st.session_state.items[new_ptr] = {"name": "필보", "price": "0"}
        st.session_state.id_ptr = new_ptr + 1
        st.rerun()

# --- 6. 계산 로직 ---
total_sales = 0
active_items = st.session_state.get('items', {})
for itm in active_items.values():
    v = re.sub(r'[^0-9]', '', itm.get("price", "0"))
    total_sales += int(v) if v else 0

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