import streamlit as st
import pandas as pd
from datetime import datetime
import time
import data_manager

def render_user_mode(worksheet):

  
    # Custom CSS for styling
    st.markdown("""
    <style>
        /* 2. 최상단 제목((주)그룹원 식사쿠폰) 위쪽 마진 제거 */
        h1 {
        margin-top: -60px !important;  /* 음수 마진으로 더 바짝 붙임 */
        padding-top: 0px !important;
        margin-bottom: 2px !important;
        }

        /* 3. 성공 메시지 출력 시 발생하는 공백 최소화 */
        div[style*="text-align: center;"] {
        margin-top: 0px !important;
        padding-top: 0px !important;
        }

        /* --- 이하 기존 스타일 유지 --- */
        [data-testid="stVerticalBlock"] > div {
        margin-top: 0px !important;
        margin-bottom: 0px !important;
        }
        
        /* 2. 일반 텍스트 및 마크다운 줄간격/여백 제거 */
        .stMarkdown p, .stWidgetLabel, label, .stRadio label, p {
            font-size: 20px !important;
            font-weight: bold !important;
            color: #66CCFF !important;
            margin: 0px !important;         /* 텍스트 상하 마진 제거 */
            padding: 0px !important;        /* 패딩 제거 */
            line-height: 1.0 !important;    /* 행 높이를 타이트하게 조정 */
        }

        /* 3. 입력창(Selectbox, DateInput) 너비 조정 및 Radio 버튼 가로 정렬 보장 */
        div[data-testid="stSelectbox"], 
        div[data-testid="stDateInput"] {
            width: 40% !important;
            margin-top: 0px !important;
            margin-bottom: 0px !important;
        }

        /* Radio 버튼은 너비를 100%로 풀어서 옵션이 가로로 배치되게 함 */
        div[data-testid="stRadio"] {
            width: 100% !important;
            margin-top: 0px !important;
            margin-bottom: 0px !important;
        }

        /* 4. 서브헤더 및 표 간격 조정 */
        h3 {
            font-size: 20px !important;
            font-weight: bold !important;
            color: #66CCFF !important;
            margin-top: 0px !important;     /* 헤더 위쪽 간격 최소화 */
            margin-bottom: 0px !important;
        }

        .custom-table {
            width: 60%;
            border-collapse: collapse;
            margin-top: 0px !important;      /* 표 위쪽 간격 제거 */
        }

        /* --- 이하 기존 스타일 유지 및 최적화 --- */

        .stSelectbox div[data-baseweb="select"] div,
        .stDateInput input,
        div[role="radiogroup"] p {
            color: #66CCFF !important;
            font-size: 20px !important; 
            font-weight: bold !important;
            line-height: 1.0 !important;
        }

        .stSelectbox span {
            color: #66CCFF !important;
        }

        /* 확인 버튼 스타일 */
        div[data-testid="stButton"] button[kind="primary"] {
            background-color: #FF8C00 !important;
            color: #66CCFF !important;
            font-size: 20px !important;
            padding: 5px 10px !important;
            width: auto !important;
            border-radius: 12px !important;
            border: 2px solid #E67E00 !important;
            margin-top: 0px !important;    /* 버튼 위쪽 간격 제거 */
        }
        
        div[data-testid="stButton"] button[kind="primary"]:active {
            transform: scale(0.9) !important;
        }

        /* 관리자 버튼 스타일 */
        div[data-testid="stButton"] button[kind="secondary"] {
            font-size: 20px !important;
            font-weight: bold !important;
            width: auto !important;
            padding: 5px 10px !important;
            border: 2px solid #ccc !important;
            color: #66CCFF !important;
            background-color: #FF8C00 !important;
        }

        .custom-table th, .custom-table td {
            color: #66CCFF;
            font-size: 20px !important; 
            font-weight: bold !important;
            padding: 4px;                  /* 표 셀 내부 간격도 살짝 줄임 */
            border-bottom: 1px solid #555;
            text-align: center !important; /* 표 안의 모든 내용을 가운데 정렬 */
        }
    </style>
    """, unsafe_allow_html=True)

    # Load data
    with st.spinner("데이터 불러오는 중..."):
        df = data_manager.get_all_tickets(worksheet)
    
    if df.empty:
        st.warning("데이터가 없습니다. 관리자에게 문의하세요.")
        return

    today = datetime.now().date()

    # Layout: Label (Left 3) | Input (Right 7)
    
    # 1. User Selection (Moved to Top)
    users = [
        '원경재', '심인숙', '이준', '이세라', '김재희', '김규화', '이민만', '황희상', '박자초', '주성보', 
        '오근영', '안현수', '정균석', '최재우', '박지훈', '김지영', '김진영',  '황찬진',  '이주현', '김선열', 
        '손태호', '김종학', '윤재흥', '김태영', '황인재', '진승훈', '김재현', '서한규', '강종원', '최재혁'
    ]
    col_u_1, col_u_2 = st.columns([2, 8], vertical_alignment="center", gap="small")
    with col_u_1:
        st.markdown("사용자")
    with col_u_2:
        user_name = st.selectbox("사용자", users, index=0, label_visibility="collapsed")    

    # 2. Usage Date
    col_d_1, col_d_2 = st.columns([2, 8], vertical_alignment="center", gap="small")
    with col_d_1:
        st.markdown("사용일")
    with col_d_2:
        use_date = st.date_input("사용일", value=today, label_visibility="collapsed")     

    # 3. Usage Time
    col_t_1, col_t_2 = st.columns([2, 8], vertical_alignment="center", gap="small")
    with col_t_1:
         st.markdown("사용타임")
    with col_t_2:
         use_time = st.radio("사용타임", ["점심", "저녁"], horizontal=True, label_visibility="collapsed")

    # Helper: Ticket Type
    col_type_1, col_type_2 = st.columns([2, 8], vertical_alignment="center", gap="small")
    with col_type_1:
        st.markdown("식권종류")
    with col_type_2:
        ticket_type = st.radio("식권종류", ["밥플러스", "빅스푼"], horizontal=True, label_visibility="collapsed")

    # 4. Ticket Number
    if ticket_type:
        unused_tickets = data_manager.get_unused_tickets(df, ticket_type)
        if not unused_tickets:
            st.warning(f"'{ticket_type}'의 사용 가능한 식권이 없습니다.")
            ticket_number = None
        else:
             col_n_1, col_n_2 = st.columns([2, 8], vertical_alignment="center", gap="small")
             with col_n_1:
                 st.markdown("식권번호")
             with col_n_2:
                ticket_number = st.selectbox("식권번호", unused_tickets, label_visibility="collapsed")     
    else:
        ticket_number = None

    # 6. Usage/Loss Toggle
    # Req: Toggle button, default "Used". "Loss" only for admin?
    # 6. Usage/Loss Toggle
    is_lost = st.toggle("분실 (체크시 분실 처리)")
    action_type = "분실" if is_lost else "사용"

    # Submit Button
    # Submit Button - Primary Type for Styling
    if st.button("확인(한번만_터치하세요)", type="primary"):
        if not ticket_number:
            st.error("식권 번호를 선택해주세요.")
        elif not user_name:
            st.error("사용자 이름을 입력해주세요.")
        else:
            # No admin check needed for "분실" per new requirements

            success = data_manager.use_ticket(
                worksheet, 
                ticket_number, 
                user_name, 
                use_time,
                str(use_date),
                note=action_type
            )
            
            if success:
                st.session_state["success_message"] = f"{ticket_type} {ticket_number}번 처리 완료!"
                st.rerun()

    # Success Message Display (Moved below button)
    if "success_message" in st.session_state:
        msg = st.session_state["success_message"]
        st.markdown(f"""
        <div style="
            text-align: left; 
            color: red; 
            font-size: 24px; 
            font-weight: bold; 
            margin-top: 0px;
            margin-left: 0px;
        ">  
            {msg}
        </div>
        """, unsafe_allow_html=True)
        # Wait 3s and clear
        time.sleep(3)
        del st.session_state["success_message"]
        st.rerun()

    # Footer Stats
    st.subheader("📊 보유 수량")
    if not df.empty:
        # Count where '비고' is not '사용'/'분실'
        # Actually `get_unused_tickets` logic: (df["비고"] == "") | (df["비고"].isna())
        mask = (df["비고"] == "") | (df["비고"].isna())
        stats = df[mask]["식권종류"].value_counts()
        
        # Convert to HTML table for full custom styling
        stats_df = stats.reset_index()
        stats_df.columns = ["식권종류", "보유 수량"] # Header names
        
        # Generate HTML
        html_table = stats_df.to_html(index=False, classes="custom-table", border=0)
        st.markdown(html_table, unsafe_allow_html=True)

    # Admin Button moved to bottom
    if st.button("관리자"):
        st.session_state["page"] = "admin_login"
        st.rerun()
















