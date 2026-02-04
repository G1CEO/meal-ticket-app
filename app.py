import os
import sys

# Auto-launch with Streamlit if run directly
if __name__ == "__main__" and "STREAMLIT_RUN" not in os.environ:
    os.environ["STREAMLIT_RUN"] = "true"
    # Execute streamlit run command with the current file
    # --browser.gatherUsageStats false suppresses the email prompt
    os.system(f"streamlit run \"{__file__}\" --browser.gatherUsageStats false")
    sys.exit()

import streamlit as st
import data_manager
import ui_user
import ui_admin

# Page Config
st.set_page_config(page_title="(주)그룹원 식사쿠폰", page_icon="")

# State Init
if "is_admin" not in st.session_state:
    st.session_state["is_admin"] = False

def main():
    # Connect to DB
    spreadsheet = data_manager.connect_to_sheet()
    
    if not spreadsheet:
        st.stop() # Stop if no connection
        
    worksheet = data_manager.fetch_log_sheet(spreadsheet)
    user_list = data_manager.get_user_list(spreadsheet)
    admin_list = data_manager.get_admin_list(spreadsheet)
        
    # Navigation / Layout replacement
    # User requested: "Home Screen 1 (Common)" and "Admin Button on Top Right"
    
    # Sidebar for easy navigation during dev, but let's try to mimic the req.
    # "Top Right Admin Button" -> Streamlit buttons are usually in flow. 
    # Can use sidebar or just a button at top.
    
    # Title (Logo removed per request)
    st.markdown("<h2 style='margin: 0; padding: 10px 0; font-size: 24px;'>(주)그룹원 식사쿠폰</h2>", unsafe_allow_html=True)

    # Routing
    current_page = st.session_state.get("page", "home")
    
    if st.session_state["is_admin"]:
        # If logged in as admin, show Admin UI
        ui_admin.render_admin_dashboard(worksheet)
    elif current_page == "admin_login":
        ui_admin.render_admin_login(admin_list)
        if st.button("홈으로 돌아가기"):
            st.session_state["page"] = "home"
            st.rerun()
    else:
        # Default Common User Mode
        ui_user.render_user_mode(worksheet, user_list)

if __name__ == "__main__":
    main()
