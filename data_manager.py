import streamlit as st
import gspread
from gspread.exceptions import APIError
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from datetime import datetime
import os

# Google Sheet ID
SHEET_ID = "18CKNYYa05EoVcfFJW7ZNvUTKnqUIL_UyXIi6pBXv8ZI"
SHEET_NAME_LOG = "식권관리대장" # Main sheet name for tickets

def connect_to_sheet():
    """
    Connects to Google Sheets using credentials from Streamlit secrets or local file.
    Returns the worksheet object.
    """
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = None
    
    try:
        # 1. First, check for local key file (Priority for Local Dev)
        if os.path.exists('service_account.json'):
            creds = ServiceAccountCredentials.from_json_keyfile_name('service_account.json', scope)
        else:
            # 2. If no local file, try Streamlit Secrets (for Cloud Deployment)
            try:
                if "gcp_service_account" in st.secrets:
                    creds_dict = st.secrets["gcp_service_account"]
                    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
            except FileNotFoundError:
                # st.secrets access raises FileNotFoundError if no secrets file exists
                pass
            except Exception:
                pass

        if creds is None:
            st.error("Google Sheet 연결 실패: 인증 정보를 찾을 수 없습니다.")
            st.info("""
            [해결 방법]
            1. 'service_account.json' 파일이 프로젝트 폴더에 있는지 확인하세요.
            2. 파일명 철자가 정확한지 확인하세요.
            3. 또는 .streamlit/secrets.toml 설정이 되어 있는지 확인하세요.
            """)
            return None
            
        client = gspread.authorize(creds)
        sheet = client.open_by_key(SHEET_ID)
        return sheet
        
    except APIError as e:
        if e.response.status_code == 429:
            st.warning("쓰기 한도 초과, 이후 재시도 요망")
            return None
        else:
            st.error(f"Google Sheet API 오류 발생: {e}")
            return None

    except Exception as e:
        import traceback
        err_msg = traceback.format_exc()
        st.error(f"Google Sheet 연결 중 오류 발생: {e}")
        st.code(err_msg)
        
        # Check if it is a specific known error
        error_str = str(e)
        if "SpreadsheetNotFound" in error_str:
             st.warning(f"❌ '{SHEET_ID}' 시트를 찾을 수 없습니다.\n구글 시트의 [공유] 설정에서 서비스 계정 이메일(client_email)을 '편집자'로 추가했는지 확인해주세요.")
             if creds:
                 try:
                     st.info(f"서비스 계정 이메일: {creds.service_account_email}")
                 except:
                     pass
        elif "403" in error_str:
             st.warning(f"❌ 권한이 없습니다 (403 Error).\n구글 시트의 [공유] 설정에서 서비스 계정 이메일을 '편집자'로 추가했는지 확인해주세요.")
             if creds:
                 try:
                     st.info(f"서비스 계정 이메일: {creds.service_account_email}")
                 except:
                     pass
                     
        return None

def fetch_log_sheet(sheet):
    """
    Retrieves the main log worksheet from the spreadsheet object.
    (Renamed to force module reload)
    """
    if sheet is None:
        return None
        
    try:
        worksheet = sheet.worksheet(SHEET_NAME_LOG)
    except:
        # Fallback to the first sheet if specific name not found
        worksheet = sheet.sheet1
    return worksheet

@st.cache_data(ttl=3600)
def get_user_list(_sheet):
    """
    Retrieves the user list from the '사용자목록' sheet.
    Assumes column A contains the names and Row 1 is header.
    Cached for 1 hour since user list rarely changes.
    Note: _sheet arg name starts with _ to tell Streamlit not to hash it.
    But actually, for cache_data, we need to be careful. 
    If sheet object changes, we want to reload. 
    However, gspread sheet object hashing might be expensive or not work well.
    Let's rely on TTL mostly.
    """
    if _sheet is None:
        return []
        
    SHEET_NAME_USERS = "사용자목록"
    try:
        worksheet = _sheet.worksheet(SHEET_NAME_USERS)
        # Get all values from the first column
        names = worksheet.col_values(1)
        
        # If list is not empty, assume first row is header and exclude it
        if len(names) > 1:
            return names[1:]
        return []
    except Exception:
        # If sheet doesn't exist or other error, return empty list
        return []
        

@st.cache_data(ttl=3600)
def get_admin_list(_sheet):
    """
    Retrieves the admin email list from the '관리자목록' sheet.
    Assumes column A contains the emails and Row 1 is header.
    Cached for 1 hour.
    """
    if _sheet is None:
        return []
        
    SHEET_NAME_ADMINS = "관리자목록"
    try:
        worksheet = _sheet.worksheet(SHEET_NAME_ADMINS)
        # Get all values from the first column
        emails = worksheet.col_values(1)
        
        # If list is not empty, assume first row is header and exclude it
        if len(emails) > 1:
            return emails[1:]
        return []
    except Exception:
        # If sheet doesn't exist or other error, return empty list
        return []


@st.cache_data(ttl=3600)
def get_admin_password(_sheet):
    """
    Retrieves the admin password from the '비밀번호' sheet (Cell A2).
    Cached for 1 hour.
    """
    if _sheet is None:
        return None
        
    SHEET_NAME_PW = "비밀번호"
    try:
        worksheet = _sheet.worksheet(SHEET_NAME_PW)
        # Fetch value from A2
        password = worksheet.acell('A2').value
        return str(password).strip() if password else None
    except Exception:
        return None


def get_all_tickets(worksheet):
    """
    Fetches all data from the sheet and returns a DataFrame.
    """
    if worksheet is None:
        return pd.DataFrame()
    
    data = worksheet.get_all_records()
    df = pd.DataFrame(data)
    
    # Ensure columns exist even if empty
    expected_cols = ["식권종류", "식권번호", "구매일", "사용일", "사용타임", "사용자", "비고"]
    for col in expected_cols:
        if col not in df.columns:
            df[col] = ""
            
    return df

def get_unused_tickets(df, ticket_type):
    """
    Returns a list of unused ticket numbers for a specific type.
    """
    if df.empty:
        return []
    
    # Filter by type and '비고' is empty or not in ['사용', '분실']
    # Assuming "비고" column stores status. Empty string implies unused.
    # Convert '비고' to string to handle potential non-string values safely
    
    # logic: Type matches AND (Note is empty)
    mask = (df["식권종류"] == ticket_type) & (
        (df["비고"] == "") | (df["비고"].isna())
    )
    
    available = df[mask]["식권번호"].sort_values().unique().tolist()
    return available

def use_ticket(worksheet, ticket_number, user_name, usage_time, date_str, note="사용"):
    """
    Updates the ticket row with usage details.
    """
    try:
        # Find the cell with the ticket number
        cell = worksheet.find(str(ticket_number))
        row = cell.row
        
        # Update columns: 사용일, 사용타임, 사용자, 비고
        headers = worksheet.row_values(1)
        col_map = {name: i+1 for i, name in enumerate(headers)}
        
        updates = []
        if "사용일" in col_map:
            updates.append({"range": gspread.utils.rowcol_to_a1(row, col_map["사용일"]), "values": [[date_str]]})
            
        if "사용타임" in col_map:
             updates.append({"range": gspread.utils.rowcol_to_a1(row, col_map["사용타임"]), "values": [[usage_time]]})

        if "사용자" in col_map:
             updates.append({"range": gspread.utils.rowcol_to_a1(row, col_map["사용자"]), "values": [[user_name]]})
             
        if "비고" in col_map:
             updates.append({"range": gspread.utils.rowcol_to_a1(row, col_map["비고"]), "values": [[note]]})
        
        if updates:
             worksheet.batch_update(updates)
             
        return True
    except APIError as e:
        if e.response.status_code == 429:
            st.warning("쓰기 한도 초과, 이후 재시도 요망")
        else:
            st.error(f"식권 처리 중 API 오류 발생: {e}")
        return False
    except Exception as e:
        st.error(f"식권 처리 중 오류 발생: {e}")
        return False

def add_new_tickets(worksheet, ticket_type, start_num, count):
    """
    Adds new tickets to the sheet.
    """
    try:
        new_rows = []
        today = datetime.now().strftime("%Y-%m-%d")
        
        for i in range(count):
            num = start_num + i
            # Row: 식권종류 | 식권번호 | 구매일 | 사용일 | 사용타임 | 사용자 | 비고
            new_rows.append([ticket_type, num, today, "", "", "", ""])
            
        worksheet.append_rows(new_rows)
        return True
    except APIError as e:
        if e.response.status_code == 429:
            st.warning("쓰기 한도 초과, 이후 재시도 요망")
        else:
            st.error(f"식권 추가 중 API 오류 발생: {e}")
        return False
    except Exception as e:
        st.error(f"식권 추가 중 오류 발생: {e}")
        return False
