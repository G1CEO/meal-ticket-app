import streamlit as st
import pandas as pd
from datetime import datetime
import time
import data_manager

def render_user_mode(worksheet):
    # Success Message Display (Custom Styled) - Check at start to allow rendering before rest of UI if needed, 
    # but more importantly to handle the auto-dismiss.
    if "success_message" in st.session_state:
        msg = st.session_state["success_message"]
        st.markdown(f"""
        <div style="
            text-align: center; 
            color: red; 
            font-size: 30px; 
            font-weight: bold; 
            margin-top: 0px;
        ">
            {msg}
        </div>
        """, unsafe_allow_html=True)
        # Wait 3s and clear
        time.sleep(3)
        del st.session_state["success_message"]
        st.rerun()
  
    # Custom CSS for styling
    st.markdown("""
    <style>
        /* Labels: 2x size, Bold, White */
        .stMarkdown p, .stWidgetLabel, label, .stRadio label, p {
            font-size: 20px !important;
            font-weight: bold !important;
            color: #66CCFF !important;
        }
        
        /* Subheader (Remaining Quantity) */
        h3 {
            font-size: 20px !important;
            font-weight: bold !important;
            color: #66CCFF !important;
        }
 
        /* 사용자, 사용일, 식권번호 입력창의 너비를 부모 대비 50%로 강제 고정 */
        div[data-testid="stSelectbox"],     
        div[data-testid="stDateInput"] {
            width: 30% !important;
        }

        /* 텍스트 크기 및 색상 스타일 (기존 유지) */
        .stSelectbox div[data-baseweb="select"] div,
        .stDateInput input,
        div[role="radiogroup"] p {
            color: #66CCFF !important;
            font-size: 20px !important; 
            font-weight: bold !important;
            line-height: 1.0 !important;
        }

        /* Specific target for Selectbox selected value */
        .stSelectbox span {
             color: #66CCFF !important;
        }

        /* Primary Button (Confirm): Wide, Reduced Height */
        div[data-testid="stButton"] button[kind="primary"] {
            background-color: #FF8C00 !important; /* Orange */
            color: #66CCFF !important;
            font-size: 20px !important;
            padding: 5px 10px !important;
            width: auto !important;
            border-radius: 12px !important;
            border: 2px solid #E67E00 !important;
            height: auto !important;
            margin-top: 4px;
        }
        div[data-testid="stButton"] button[kind="primary"]:hover {
            background-color: #FFA500 !important;
            border-color: #FF8C00 !important;
        }

        /* Secondary Button (Default/Admin): Large size, White Text */
        div[data-testid="stButton"] button[kind="secondary"] {
             font-size: 20px !important;
             font-weight: bold !important;
             width: auto !important;
             height: auto !important;
             white-space: nowrap !important;
             padding: 5px 10px !important;
             border: 2px solid #ccc !important;
             color: #66CCFF !important;
             background-color: #FF8C00 !important;
        }

        /* Custom Table Styling for Stats */
        .custom-table {
            width: 50%;
            border-collapse: collapse;
            margin-top: 5px;
        }
        .custom-table th {
            background-color: #333333; /* Dark Grey Header */
            color: #66CCFF;
            font-size: 20px !important; 
            font-weight: bold !important;
            padding: 5px;
            text-align: left;
            border-bottom: 1px solid #555;
        }
        .custom-table td {
            color: #66CCFF;
            font-size: 20px !important; 
            font-weight: bold !important;
            padding: 5px;
            border-bottom: 1px solid #555;
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
    col_u_1, col_u_2 = st.columns([1, 9], vertical_alignment="center")
    with col_u_1:
        st.markdown("사용자")
    with col_u_2:
        user_name = st.selectbox("사용자", users, index=0, label_visibility="collapsed")    

    # 2. Usage Date
    col_d_1, col_d_2 = st.columns([1, 9], vertical_alignment="center")
    with col_d_1:
        st.markdown("사용일")
    with col_d_2:
        use_date = st.date_input("사용일", value=today, label_visibility="collapsed")     

    # 3. Usage Time
    col_t_1, col_t_2 = st.columns([1, 9], vertical_alignment="center")
    with col_t_1:
         st.markdown("사용타임")
    with col_t_2:
         use_time = st.radio("사용타임", ["점심", "저녁"], horizontal=True, label_visibility="collapsed")

    # Helper: Ticket Type
    col_type_1, col_type_2 = st.columns([1, 9], vertical_alignment="center")
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
             col_n_1, col_n_2 = st.columns([1, 9], vertical_alignment="center")
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
    if st.button("확인(한번만_터치하세요)", type="secondary"):
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

    # (Success Message Display moved to top)

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


