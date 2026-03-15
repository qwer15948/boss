import streamlit as st

st.title("아이온2 필보 정산기")
st.caption("판매자 2%+20% / 팀원 2%+10% 수수료 모두 반영")

# 입력창
prices_str = st.text_input("아이템 총 판매 가격 (만원 단위)", "750 750")
k = st.number_input("총 인원 (판매자 포함)", min_value=1, value=6)
a = st.number_input("추가적으로 빼야할 금액 (원 단위)", min_value=0)

# [계산 로직]
total_sales = sum([int(p) for p in prices_str.split() if p.strip()]) * 10000

# 판매자 순수익 (거래소 80% - 등록비 2%)
pure_profit = total_sales * 0.78

listing_price = (pure_profit / (k - 0.12)) - a

# 인당 최종 실수령액 (X = 등록가에서 수령수수료 10% 및 등록비 2% 제외)
real_share = listing_price * 0.88

st.divider()
col1, col2 = st.columns(2)
with col1:
    st.metric("인당 최종 실수령액", f"{int(real_share):,} 원")
    st.caption("등록비/수수료 뺀 진짜 이득")
with col2:
    st.metric("인당 등록 가격", f"{int(listing_price):,} 원")
    st.caption("거래소에 위 금액대로 올려주세요.")

with st.expander("상세히 보기"):
    st.write(f"**1. 판매 아이템 총 판매액:** {total_sales:,}원")
    st.write(f"**2. 판매자 순수 정산금:** {int(pure_profit):,}원")
    st.caption("(거래소 정산 80% - 본인 등록비 2% 반영)")
    
    st.write("---")
    
    st.write(f"**3. 팀원 개별 등록 가격:** {int(listing_price):,}원")
    if a > 0:
        st.caption(f"(추가 차감액 {a:,}원이 반영된 금액입니다.)")
    
    # 판매자가 팀원에게 보내고 남은 돈 계산
    total_transfer = listing_price * (k - 1)
    seller_pocket = pure_profit - total_transfer
    
    st.write(f"**4. 정산금 분배 결과:**")
    st.write(f"- 판매자가 팀원({k-1}명)에게 보낼 총액: {int(total_transfer):,}원")
    st.write(f"- 판매자 본인이 가질 잔액: **{int(seller_pocket):,}원**")
    st.write(f"- 팀원 개별 최종 실수령액: **{int(real_share):,}원**")