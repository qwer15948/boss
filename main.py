import streamlit as st
import re
import uuid

# 1. 페이지 설정
st.set_page_config(page_title="아이온2 정산기", page_icon="🎲", layout="wide")

# 2. 세션 초기화 (딕셔너리 구조로 변경하여 데이터 독립성 보장)
if 'items' not in st.session_state:
    # 각 아이템은 고유 ID를 키로 가짐
    st.session_state.items = {
        str(uuid.uuid4()): {"name": "필보", "price": "7,500,000"}
    }

# --- 3. 커스텀 CSS (카드 디자인 및 X버튼 정밀 보정) ---
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

    .label-box {
        color: #AAA; font-size: 14px; font-weight: bold; white-space: nowrap;
        display: flex; align-items: center; height: 42px;
    }
    .item-badge {
        background-color: #FFB800; color: #000; border-radius: 50%;
        width: 22px; height: 22px; display: flex; align-items: center;
        justify-content: center; font-weight: bold; font-size: 11px;
        margin-top: 10px;
    }

    div[data-testid="stTextInput"] label { display: none !important; }
    input {
        background-color: #1E1E1E !important;
        border: 1px solid #444 !important;
        border-radius: 8px !important;
        color: white !important;
    }

    /* 삭제 버튼(X) 정중앙 완벽 정렬 및 크기 고정 */
    div.stButton > button[key^="del_"] {
        height: 42px !important;
        width: 42px !important;
        padding: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        background-color: #333 !important;
        border: 1px solid #444 !important;
        color: #888 !important;
        font-size: 18px !important;
        line-height: 1 !important;
        border-radius: 8px !important;
    }
    div.stButton > button[key="add_btn"] {
        background-color: #333 !important;
        color: #FFB800 !important;
        border: 1px solid #FFB800 !important;
        height: 50px !important;
        font-weight: bold !important;
        border-radius: 10px !important;
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

def add_item():
    new_id = str(uuid.uuid4())
    st.session_state.items[new_id] = {"name": "필보", "price": "0"}

def delete_item(item_id):
    if item_id in st.session_state.items:
        del st.session_state.items[item_id]
        st.rerun()

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
    
    display_num = 1
    # 딕셔너리를 순회하며 카드 생성
    for item_id, item_info in list(st.session_state.items.items()):
        with st.container(border=True):
            st.markdown('<div class="item-card-marker"></div>', unsafe_allow_html=True)
            
            # 1행
            r1_c1, r1_c2, r1_c3 = st.columns([0.8, 8, 1.2])
            with r1_c1:
                st.markdown(f'<div class="item-badge">{display_num}</div>', unsafe_allow_html=True)
            with r1_c2:
                # 위젯 키에 UUID를 사용하여 데이터 꼬임 방지
                st.session_state.items[item_id]["name"] = st.text_input(
                    "보스명", value=item_info["name"], key=f"ni_{item_id}"
                )
            with r1_c3:
                # 삭제 버튼
                if st.button("✕", key=f"del_{item_id}"):
                    delete_item(item_id)
            
            # 2행
            r2_c1, r2_c2, r2_c3 = st.columns([1.8, 7.2, 1])
            with r2_c1:
                st.markdown('<div class="label-box">판매가</div>', unsafe_allow_html=True)
            with r2_c2:
                raw_price = st.text_input(
                    "가격", value=item_info["price"], key=f"pi_{item_id}"
                )
                # 입력 시 즉시 콤마 적용
                formatted = format_comma(raw_price)
                if formatted != raw_price:
                    st.session_state.items[item_id]["price"] = formatted
                    st.rerun()
                else:
                    st.session_state.items[item_id]["price"] = raw_price
            with r2_c3:
                st.markdown('<div class="label-box">원</div>', unsafe_allow_html=True)
            
            display_num += 1

    st.button("＋ 아이템 추가", key="add_btn", on_click=add_item, use_container_width=True)

# --- 6. 계산 로직 ---
total_sales = 0
for item in st.session_state.items.values():
    val = re.sub(r'[^0-9]', '', item["price"])
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