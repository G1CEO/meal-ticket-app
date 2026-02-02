import streamlit as st
import pandas as pd
import data_manager

ADMIN_EMAILS = ["wkj1003@gmail.com", "sis06200915@gmail.com","linpap1101@gmail.com]

def render_admin_login():
    st.header("🔒 관리자 로그인")
    
    # Custom CSS for Login Styling
    st.markdown("""
    <style>
        /* General Text */
        .stMarkdown p {
            font-size: 20px !important;
            color: #66CCFF !important;
        }

        /* 1. Input Labels & Button: Huge (20px) & Bold */
        /* Targets: Text Input Labels, All Streamlit Buttons (Primary & Secondary) */
        .stWidgetLabel, label, .stButton button {
            font-size: 20px !important;
            font-weight: bold !important;
            color: #66CCFF !important;
            padding: 15px 40px !important;
            line-height: 1.0 !important;
        }
        
        /* Ensure button background is handled by theme or specific overrides */
        /* Secondary buttons (default) usually transparent in dark mode */
        div[data-testid="stButton"] button[kind="secondary"] {
             border: 2px solid #ccc !important;
             color: #66CCFF !important;
        }

        /* 2. Alert/Info Box: Smaller (20px) */
        .stAlert p, .stAlert {
             font-size: 20px !important;
             font-weight: bold !important;
             color: #66CCFF !important; /* Ensure text is #66CCFF even in alert */
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.info("관리자 외 로그인 시도 금지")
    
    email = st.text_input("아이디")
    if st.button("로그인"):
        if email.strip() in ADMIN_EMAILS:
            st.session_state["is_admin"] = True
            st.session_state["admin_email"] = email
            st.success("로그인 성공!")
            st.rerun()
        else:
            st.error("관리자 권한이 없는 계정입니다.")

def render_admin_dashboard(worksheet):
    st.header("⚙️ 관리자 모드")
    
    # Custom CSS for Admin Styling
    st.markdown("""
    <style>
        /* Labels and Text: 1.5x size (~20px), Bold, White */
        .stMarkdown p, .stWidgetLabel, label, .stRadio label, p, .stTextInput input, .stNumberInput input {
            font-size: 20px !important;
            font-weight: bold !important;
            color: #66CCFF !important;
        }

        /* Specific fix for Selectbox/Input height to accommodate larger text if needed */
        .stSelectbox div[data-baseweb="select"] div {
            font-size: 20px !important;
            font-weight: bold !important;
            color: #66CCFF !important;
        }

        /* Custom Table Styling */
        .custom-admin-table {
            width: 50%;
            border-collapse: collapse;
            margin-top: 10px;
        }
        .custom-admin-table th {
            background-color: #333333; /* Dark Grey */
            color: #66CCFF;
            font-size: 20px !important;
            font-weight: bold !important;
            padding: 12px;
            text-align: left;
            border-bottom: 2px solid #555;
        }
        .custom-admin-table td {
            color: #66CCFF;
            font-size: 20px !important;
            font-weight: bold !important;
            padding: 12px;
            border-bottom: 1px solid #555;
        }
    </style>
    """, unsafe_allow_html=True)

    st.write(f"로그인 계정: {st.session_state.get('admin_email')}")
    
    # Buttons: Logout and Google Sheet Link side-by-side
    # Adjusted ratio to prevent 'Logout' button text wrapping (large font)
    btn_col1, btn_col2 = st.columns([4, 6])
    with btn_col1:
        if st.button("나가기"):
            st.session_state["is_admin"] = False
            st.session_state["admin_email"] = None
            st.rerun()
    with btn_col2:
        st.link_button("구글시트 링크", "https://docs.google.com/spreadsheets/d/18CKNYYa05EoVcfFJW7ZNvUTKnqUIL_UyXIi6pBXv8ZI/edit?usp=sharing")
        
    st.divider()
    
    # 1. Add Tickets
    st.subheader("➕ 식권 추가 (Add Tickets)")
    
    col1, col2 = st.columns(2)
    with col1:
        # Ticket types from existing
        # Needed for inventory view below
        df = data_manager.get_all_tickets(worksheet)
        # existing_types = df["식권종류"].unique().tolist()
        # existing_types = [t for t in existing_types if t]
        
        # Req: 식권 종류 입력 : [목록에서 선택]밥플러스, 빅스푼
        ticket_type = st.selectbox("식권 종류 선택", ["밥플러스", "빅스푼"])
            
    with col2:
        start_num = st.number_input("시작 식권 번호", min_value=1, value=1001, step=1)
        count = st.number_input("생성 개수", min_value=1, value=50, step=1)

    if st.button("식권 생성 (Add)"):
        if not ticket_type:
            st.error("식권 종류를 입력해주세요.")
        else:
            success = data_manager.add_new_tickets(worksheet, ticket_type, int(start_num), int(count))
            if success:
                st.success(f"{ticket_type} 식권 {count}장 ({start_num}~{int(start_num)+int(count)-1}) 생성 완료!")
                st.rerun()

    st.divider()

    # 2. View Inventory (Unused Tickets)
    st.subheader("📋 보유 식권 목록 (Inventory)")
    
    if not df.empty:
        # Group by type and list numbers
        # Filter unused
        mask = (df["비고"] == "") | (df["비고"].isna())
        unused_df = df[mask]
        
        if unused_df.empty:
            st.info("보유 중인 식권이 없습니다.")
        else:
            # Stats Summary
            # Stats Summary
            # Stats Summary
            # Use HTML table instead of dataframe
            # Use HTML table instead of dataframe
            stats = unused_df["식권종류"].value_counts().reset_index()
            stats.columns = ["식권종류", "잔여수량"]
            html = stats.to_html(index=False, classes="custom-admin-table", border=0)
            st.markdown(html, unsafe_allow_html=True)
            
            # List details (Expandable)
            st.write("상세 목록:")
            for t_type in unused_df["식권종류"].unique():
                with st.expander(f"{t_type} 목록 보기"):
                    nums = unused_df[unused_df["식권종류"] == t_type]["식권번호"].sort_values().tolist()
                    st.write(f"개수: {len(nums)}")
                    st.write(", ".join(map(str, nums)))

    st.divider()
    



