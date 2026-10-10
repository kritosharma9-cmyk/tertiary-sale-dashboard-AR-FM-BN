import pandas as pd
import streamlit as st
import numpy as np
import plotly.express as px
import plotly.graph_objects as go  
import io
import os
import shutil
from datetime import datetime, timedelta

# Page Configuration
st.set_page_config(page_title="Tertiary Sale Dashboard", layout="wide", page_icon="📈")

# ==========================================
# 💾 1. USER DATABASE & RIGHTS LOGIC
# ==========================================
def get_users_db():
    db_file = "users_db.csv"
    if not os.path.exists(db_file):
        default_data = {
            "Username": ["GOD (ADMIN)", "1. BOSS", "2. CHAUHAN SIR", "3. MUNIT", "4. AJAY", "5. ABHISHEK", "6. RAVINDER", "7. BARINDER (ASM)", "8. RAJESH SINGH (ASM)", "9. SULABH (RSM)", "10. ABHISHEK (RSM)"],
            "Password": ["GOD@123", "Boss@123", "CHAUHAN@123", "MUNIT@123", "AJAY@123", "ABHI@123", "RAVI@123", "BARINDER@123", "RAJESH@123", "SULABH@123", "ABHI@123"],
            "Role": ["ADMIN", "ALL", "ALL", "ALL", "ALL", "ALL", "ALL", "AR", "FM", "FM", "AR"],
            "Allowed_Columns": ["ALL"] * 11,
            "Allowed_Tabs": ["ALL"] * 11,
            "Allowed_Features": ["ALL"] * 11
        }
        df = pd.DataFrame(default_data)
        df.to_csv(db_file, index=False)
        return df
    else:
        df = pd.read_csv(db_file)
        if 'Allowed_Columns' not in df.columns: df['Allowed_Columns'] = "ALL"
        if 'Allowed_Tabs' not in df.columns: df['Allowed_Tabs'] = "ALL"
        if 'Allowed_Features' not in df.columns: df['Allowed_Features'] = "ALL"
        return df

# ==========================================
# 🔒 2. SECURITY ACCESS SYSTEM
# ==========================================
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state.password_correct = False
    if "user_role" not in st.session_state:
        st.session_state.user_role = None
    if "selected_user" not in st.session_state:
        st.session_state.selected_user = None

    if st.session_state.password_correct:
        return True

    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        with st.container(border=True):
            st.markdown("<h2 style='text-align: center;'>🔐 Dashboard Login</h2>", unsafe_allow_html=True)
            
            users_df = get_users_db()
            usernames_list = ["-- Apna Naam Select Karein --"] + users_df['Username'].tolist()
            sel_user = st.selectbox("👤 Username:", usernames_list)
            user_password = st.text_input("Enter Security Password:", type="password")
            
            if st.button("Login 🚀", use_container_width=True):
                if sel_user == "-- Apna Naam Select Karein --":
                    st.warning("⚠️ Kripya apna Username select karein.")
                else:
                    user_row = users_df[users_df['Username'] == sel_user].iloc[0]
                    if str(user_password) == str(user_row['Password']):
                        st.session_state.password_correct = True
                        st.session_state.user_role = user_row['Role']
                        st.session_state.selected_user = sel_user
                        st.rerun()
                    else:
                        st.error("❌ Invalid Password")
    return False

if not check_password():
    st.stop()

# Fetch Active User Rights
current_users_df = get_users_db()
logged_in_user_row = current_users_df[current_users_df['Username'] == st.session_state.selected_user].iloc[0]
allowed_columns_str = logged_in_user_row.get('Allowed_Columns', "ALL")
allowed_tabs_str = logged_in_user_row.get('Allowed_Tabs', "ALL")
allowed_features_str = logged_in_user_row.get('Allowed_Features', "ALL")

def check_feature_access(feature_name):
    if pd.isna(allowed_features_str) or allowed_features_str == "ALL": return True
    if "ALL" in [f.strip() for f in allowed_features_str.split(",")]: return True
    return feature_name in [f.strip() for f in allowed_features_str.split(",")]

def check_tab_access(tab_name):
    if pd.isna(allowed_tabs_str) or allowed_tabs_str == "ALL": return True
    if "ALL" in [t.strip() for t in allowed_tabs_str.split(",")]: return True
    return tab_name in [t.strip() for t in allowed_tabs_str.split(",")]

# ==========================================
# 📊 MAIN DASHBOARD
# ==========================================
st.title("Tertiary Sale Dashboard 📊")

# ==========================================
# 📆 GLOBAL SCOPE: DYNAMIC TIME & SEQUENCE LOGIC
# ==========================================
today = datetime.now()
target_date = today - timedelta(days=1)
current_month_num = target_date.month
current_day_limit = target_date.day
current_date_str = target_date.strftime("%d-%b")

passed_months = [m for m in range(4, 13) if m < current_month_num] if current_month_num >= 4 else [m for m in range(4, 13)] + [m for m in range(1, current_month_num)]

m_sequence = ['April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December', 'January', 'February', 'March']

months_to_show = []
temp_date = datetime(2025, 4, 1)
while len(months_to_show) < 4:
    if temp_date.month == current_month_num:
        months_to_show.append(temp_date.strftime('%B'))
        break
    months_to_show.append(temp_date.strftime('%B'))
    temp_date = (temp_date.replace(day=1) + timedelta(days=32)).replace(day=1)
    if len(months_to_show) == 4: break

# Custom CSS for Tabs & Print Layout
st.markdown("""
<style>
    button[data-baseweb="tab"] {
        border: 2px solid #e0e0e0 !important;
        border-radius: 8px !important;
        padding: 10px 16px !important;
        margin: 5px !important;
        background-color: #f8f9fa !important;
        min-width: 140px !important;
        font-weight: bold !important;
        font-size: 15px !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        background-color: #1F4E79 !important;
        color: white !important;
        border-color: #1F4E79 !important;
    }
    div[data-testid="stTabs"] div[role="tablist"] {
        display: flex !important;
        flex-wrap: wrap !important;
        overflow-x: hidden !important;
    }
    
    /* PDF Print Optimization */
    @media print {
        section[data-testid="stSidebar"] { display: none !important; }
        header[data-testid="stHeader"] { display: none !important; }
        .stButton { display: none !important; }
        .stDownloadButton { display: none !important; }
    }
</style>
""", unsafe_allow_html=True)

# Download Function
def to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Data')
    return output.getvalue()

def format_indian_num(val, is_currency=False, prefix="₹"):
    if not isinstance(val, (int, float, np.number)) or pd.isna(val):
        return str(val)
    is_negative = val < 0
    val = abs(val)
    s = f"{val:.0f}"
    if len(s) <= 3:
        res = s
    else:
        res = s[-3:]
        remaining = s[:-3]
        while remaining:
            res = remaining[-2:] + "," + res
            remaining = remaining[:-2]
    if is_negative:
        res = "-" + res
    return f"{prefix}{res}" if is_currency else res

def clean_df_for_single_mode(df, b_y):
    cols_to_keep = []
    for c in df.columns:
        c_str = str(c)
        if b_y in c_str or 'Gr(%)' in c_str or 'GR(%)' in c_str or 'LY ' in c_str or c_str.startswith('LY_'):
            continue
        cols_to_keep.append(c)
    return df[cols_to_keep]

# 🚀 CACHE DATA ENABLED
@st.cache_data
def load_data(file_name):
    try:
        df = pd.read_excel(file_name, engine='openpyxl')
    except FileNotFoundError:
        st.error(f"⚠️ {file_name} nahi mili.")
        st.stop()
        
    df.columns = df.columns.str.strip().str.upper()
    df['SALEVAL'] = pd.to_numeric(df['SALEVAL'].astype(str).str.replace(',', ''), errors='coerce').fillna(0)
    df['QTY'] = pd.to_numeric(df['QTY'].astype(str).str.replace(',', ''), errors='coerce').fillna(0)
    
    disc_like_cols = [c for c in df.columns if any(k in c for k in ['DISC', 'DISCOUNT'])]
    for dc in disc_like_cols:
        df[dc] = pd.to_numeric(df[dc].astype(str).str.replace(',', ''), errors='coerce').fillna(0)

    df['BILLDATE'] = pd.to_datetime(df['BILLDATE'], errors='coerce').fillna(pd.to_datetime('2000-01-01'))
    df['MONTH_NAME'] = df['BILLDATE'].dt.strftime('%B')
    df['YEAR2'] = df['YEAR2'].astype(str)
    
    text_cols = ['FORMAL/CASUAL', 'EOSS/FRESH', 'SEASON', 'FIT', 'CATEGORY', 'MANAGER', 'STATE', 'STATUS', 'CUSTOMERNAMEACTIVE']
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).replace(r'[\xa0\t\n\r]', ' ', regex=True)
            df[col] = df[col].str.replace(r'\s+', ' ', regex=True)
            df[col] = df[col].str.strip().str.upper()
            
    if 'CUSTOMERNAMEACTIVE' in df.columns:
        current_time = datetime.now()
        mask_anomaly = (df['CUSTOMERNAMEACTIVE'].str.contains('MOM', na=False)) & \
                       ((df['BILLDATE'].dt.year > current_time.year) | \
                        ((df['BILLDATE'].dt.year == current_time.year) & (df['BILLDATE'].dt.month > current_time.month)))
        
        df.loc[mask_anomaly, 'SALEVAL'] = 0
        df.loc[mask_anomaly, 'QTY'] = 0
        for dc in disc_like_cols:
            df.loc[mask_anomaly, dc] = 0
            
    return df

def style_dataframe(df):
    sale_props = {'background-color': '#d4edda', 'border': '1px solid #28a745'}
    growth_props = {'background-color': '#ebf7ed', 'border': '1px solid #a9d08e'}
    styler = df.style.hide(axis="index")
    for col in df.columns:
        if 'GR(%)' in col.upper():
            styler = styler.set_properties(**growth_props, subset=[col])
        elif 'SALE' in col.upper() or ('LEDGER' in col.upper() and 'QTY' not in col.upper()):
            styler = styler.set_properties(**sale_props, subset=[col])
    return styler

def calc_growth(base, comp):
    if base == 0:
        if comp == 0: return 0.0
        return np.inf if comp > 0 else np.nan
    return (comp - base) / base * 100

def calc_growth_series(base_s, comp_s):
    base_s = base_s.astype(float)
    comp_s = comp_s.astype(float)
    with np.errstate(divide='ignore', invalid='ignore'):
        result = (comp_s - base_s) / base_s.replace(0, np.nan) * 100
    zero_base = base_s == 0
    result = result.mask(zero_base & (comp_s == 0), 0.0)
    result = result.mask(zero_base & (comp_s > 0), np.inf)
    return result

def format_cell(x, col_name):
    if not isinstance(x, (int, float, np.number)): return x
    if "Gr(%)" in col_name:
        if x == np.inf: return "🆕 New"
        if pd.isna(x): return "N/A"
        return f"📈 🟢 {x:.0f}%" if x > 0 else f"📉 🔴 {abs(x):.0f}%" if x < 0 else "➖ 0%"
    if pd.isna(x): return "N/A"
    if "SALE" in col_name.upper() or ("LEDGER" in col_name.upper() and "QTY" not in col_name.upper()):
        return format_indian_num(x, is_currency=True)
    return format_indian_num(x, is_currency=False)

def make_fy_html(val_str, gr_val, label, is_disc=False):
    if pd.isna(gr_val):
        gr_html = ""
    else:
        fc = "#28a745" if (gr_val <= 0 if is_disc else gr_val >= 0) else "#dc3545"
        gr_html = f" (<span style='color: {fc}; font-weight:bold;'>{gr_val:+.1f}%</span>)"
    return f"<div style='font-size: 13.5px; color: #555; margin-top: 3px;'><b>{label}:</b> {val_str}{gr_html}</div>"

wrapper = "<div style='margin-top: -15px;'>{}</div>"

# ==========================================
# 🏢 BRAND / FILE SELECTOR (ORIGINAL SIDEBAR)
# ==========================================
st.sidebar.markdown("### 🏢 Brand / Data Source")
available_files = [f for f in os.listdir() if f.endswith('.xlsx') and not f.startswith('~') and not f.startswith('backup_')]

if not available_files:
    st.error("⚠️ Koi Excel (.xlsx) file nahi mili is folder mein! Kripya Excel files upload karein.")
    st.stop()

# File Selector logic controlled by Admin Rights
if check_feature_access("File Selector"):
    selected_file = st.sidebar.selectbox("Select Excel File:", available_files)
else:
    selected_file = available_files[0]
    st.sidebar.info(f"Fixed View: {selected_file}")

# Strict Ram Memory Lock
if "cached_data" not in st.session_state or st.session_state.get("cached_file") != selected_file:
    with st.spinner("🚀 Loading Data into Fast Cache..."):
        st.session_state.cached_data = load_data(selected_file)
        st.session_state.cached_file = selected_file

sheet_data = st.session_state.cached_data

# Reload Data logic controlled by Admin Rights
if check_feature_access("Reload Data Button"):
    if st.sidebar.button("🔄 Force Reload / Refresh Data", use_container_width=True):
        with st.spinner("🔄 Refreshing Data into Fast Cache..."):
            st.cache_data.clear()
            st.session_state.cached_data = load_data(selected_file)
        st.rerun()
    st.sidebar.caption("Data RAM mein locked hai (Super Fast). Naya data dekhne ke liye 'Force Reload' dabayein.")

# ==========================================
# 📤 APPEND / UPDATE NEW DATA (ORIGINAL SIDEBAR)
# ==========================================
if check_feature_access("File Upload Feature"):
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"### 📤 Add New Sales to: {selected_file}")
    st.sidebar.caption("Yahan nayi Excel upload karein. Iska data upar select ki gayi file mein automatic add ho jayega.")

    backup_file = f"backup_{selected_file}"
    uploaded_file = st.sidebar.file_uploader("Upload New Month Sales (.xlsx)", type=['xlsx'])

    if uploaded_file is not None:
        if st.sidebar.button("Merge & Update Data 🚀", use_container_width=True):
            try:
                with st.spinner('Data merge ho raha hai...'):
                    shutil.copyfile(selected_file, backup_file)
                    df_existing = pd.read_excel(selected_file, engine='openpyxl')
                    df_new = pd.read_excel(uploaded_file, engine='openpyxl')
                    df_combined = pd.concat([df_existing, df_new], ignore_index=True)
                    df_combined.drop_duplicates(inplace=True)
                    df_combined.to_excel(selected_file, index=False, engine='openpyxl')
                    
                    st.session_state.cached_data = load_data(selected_file)
                    
                st.sidebar.success(f"✅ Nayi sale ka data '{selected_file}' mein successfully add ho gaya!")
                st.rerun()
                
            except Exception as e:
                st.sidebar.error(f"❌ Error aaya: {e}")

    if os.path.exists(backup_file):
        st.sidebar.markdown("---")
        st.sidebar.warning("⚠️ Kya aapse galat file update ho gayi thi?")
        if st.sidebar.button("Undo Last Upload ↩️ (Restore)", use_container_width=True):
            try:
                shutil.copyfile(backup_file, selected_file)
                os.remove(backup_file)
                st.session_state.cached_data = load_data(selected_file)
                st.sidebar.success("✅ Undo successful! Purana data wapas aa gaya hai.")
                st.rerun()
            except Exception as e:
                st.sidebar.error(f"❌ Undo fail ho gaya: {e}")

# ==========================================
# 🔍 SIDEBAR FILTERS FORM (ORIGINAL SIDEBAR)
# ==========================================
st.sidebar.markdown("---")
st.sidebar.markdown("### 🎯 Global Filters")

with st.sidebar.form(key='global_filter_form'):
    
    # Checkbox to Toggle Comparison Mode
    if check_feature_access("Compare LY Toggle"): compare_mode = st.checkbox("🔄 Enable Comparison (LY)", value=True)
    else: compare_mode = False
    
    st.markdown("**⚡ Quick Range Shortcut**")
    if check_feature_access("Quick Range Preset"): shortcut = st.selectbox("Select Preset:", ["None (Use Custom Dates Below)", "This Month", "Last Month", "Year-to-Date (YTD)"])
    else: shortcut = "None (Use Custom Dates Below)"

    st.markdown("**1. Selected Period (Target/TY)**")
    col_d1, col_d2 = st.columns(2)
    
    if shortcut == "This Month":
        def_ty_start = today.replace(day=1)
        def_ty_end = today
    elif shortcut == "Last Month":
        first_day_this_month = today.replace(day=1)
        def_ty_end = first_day_this_month - timedelta(days=1)
        def_ty_start = def_ty_end.replace(day=1)
    elif shortcut == "Year-to-Date (YTD)":
        def_ty_start = datetime(today.year if today.month >= 4 else today.year - 1, 4, 1)
        def_ty_end = today
    else:
        def_ty_start = datetime(today.year, today.month, 1)
        def_ty_end = today

    ty_start = col_d1.date_input("Start Date (TY)", def_ty_start)
    ty_end = col_d2.date_input("End Date (TY)", def_ty_end)
    
    if compare_mode:
        st.markdown("**2. Base Period (Last Year/LY)**")
        col_d3, col_d4 = st.columns(2)
        try: ly_start_default = ty_start.replace(year=ty_start.year - 1)
        except ValueError: ly_start_default = ty_start.replace(year=ty_start.year - 1, day=28)
            
        try: ly_end_default = ty_end.replace(year=ty_end.year - 1)
        except ValueError: ly_end_default = ty_end.replace(year=ty_end.year - 1, day=28)
        
        ly_start = col_d3.date_input("Start Date (LY)", ly_start_default)
        ly_end = col_d4.date_input("End Date (LY)", ly_end_default)
    else:
        ly_start = ty_start
        ly_end = ty_end
    
    ty_start_dt = pd.to_datetime(ty_start)
    ty_end_dt = pd.to_datetime(ty_end)
    ly_start_dt = pd.to_datetime(ly_start)
    ly_end_dt = pd.to_datetime(ly_end)
    
    comp_y = str(ty_start.year)
    base_y = str(ly_start.year) if compare_mode else "N/A_LY"
    
    if comp_y == base_y and compare_mode:
        comp_y = comp_y + " (TY)"
        base_y = base_y + " (LY)"

    st.markdown("---")
    
    all_columns = list(sheet_data.columns)
    guess_idx = 0
    for i, c in enumerate(all_columns):
        if c in ['BILLDATE', 'MONTH_NAME', 'YEAR2']:
            continue
        if any(k in c for k in ['BILLNO', 'INVOICENO', 'BILL_NO', 'INVOICE_NO', 'BILL NO', 'INVOICE NO', 'BILL', 'INVOICE', 'NUMBER', 'INV']):
            guess_idx = i
            break
    selected_bill_col = st.selectbox("🧾 Select Bill/Invoice Column:", all_columns, index=guess_idx)
    
    st.markdown("---")
    possible_disc_cols = [c for c in all_columns if any(k in c for k in ['DISC', 'DISCOUNT'])]
    if possible_disc_cols:
        guess_disc = 0
        for i, c in enumerate(possible_disc_cols):
            if c == 'DISCOUNT' or c == 'DISC' or 'VALUE' in c:
                guess_disc = i
                break
        selected_disc_col = st.selectbox("🏷️ Select Discount Column:", possible_disc_cols, index=guess_disc)
    else:
        selected_disc_col = None
    
    st.markdown("---")
    search_cust = st.text_input("🔍 Search Customer Name:").strip().upper()
    
    filter_cols = ['MONTH_NAME', 'CUSTOMERNAMEACTIVE', 'MANAGER', 'CATEGORY', 'FIT', 'SEASON', 'STATE', 'STATUS', 'EOSS/FRESH', 'FORMAL/CASUAL']
    selected_filters = {}
    
    for col in filter_cols:
        if col in sheet_data.columns:
            unique_vals = sorted([str(x) for x in sheet_data[col].dropna().unique()])
            selected_filters[col] = st.multiselect(f"Filter by {col.replace('_', ' ').title()}:", unique_vals, default=None)
            
    submit_button = st.form_submit_button(label='Apply Filters 🚀', use_container_width=True)

# 📄 PDF DOWNLOADER BUTTON
if check_feature_access("PDF Export Button"):
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📄 Export to PDF")
    if st.sidebar.button("🖨️ Save Dashboard as PDF", use_container_width=True, type="primary"):
        st.components.v1.html(
            """
            <script>
                window.parent.print();
            </script>
            """,
            height=0
        )
    st.sidebar.caption("💡 Tip: Jab Print window aaye, toh Destination ko 'Save as PDF' aur Layout ko 'Landscape' select karein.")
# Application of Filters
filtered_df = sheet_data.copy()

if search_cust:
    filtered_df = filtered_df[filtered_df['CUSTOMERNAMEACTIVE'].astype(str).str.contains(search_cust, case=False, na=False)]

for col, selected_vals in selected_filters.items():
    if len(selected_vals) > 0:
        filtered_df = filtered_df[filtered_df[col].astype(str).isin(selected_vals)]

# 🆕 EXCEL-STYLE SLICER & PREMIUM BLUE TAGS DISPLAY
if search_cust:
    matched_parties = sorted(filtered_df['CUSTOMERNAMEACTIVE'].dropna().unique().tolist())
    
    if matched_parties:
        with st.expander("🎛️ Click Here to Filter Specific Stores (Excel-Style Slicer)", expanded=False):
            selected_parties = st.multiselect(
                "Remove stores by clicking 'x' or select specific ones:",
                options=matched_parties,
                default=matched_parties
            )
        if selected_parties:
            filtered_df = filtered_df[filtered_df['CUSTOMERNAMEACTIVE'].isin(selected_parties)]
        else:
            filtered_df = filtered_df.iloc[0:0] 
            
        if selected_parties:
            num_stores = len(selected_parties)
            tags_html = "".join([f"<span style='background-color: #e3f2fd; color: #1565c0; padding: 5px 12px; border-radius: 15px; font-size: 13px; font-weight: 500; border: 1px solid #90caf9; display: inline-block; margin: 3px;'>{party}</span>" for party in selected_parties])
            
            st.markdown(f"""
            <div style='background-color: #ffffff; border: 1px solid #e0e0e0; border-radius: 8px; padding: 15px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);'>
                <div style='font-size: 16px; font-weight: bold; color: #1F4E79; margin-bottom: 12px; border-bottom: 1px solid #f0f0f0; padding-bottom: 8px;'>
                    🏬 Viewing Data For: "{search_cust}" 
                    <span style='background-color: #ffebee; color: #c62828; padding: 3px 8px; border-radius: 10px; font-size: 12px; margin-left: 8px;'>{num_stores} Stores Selected</span>
                </div>
                <div style='display: flex; flex-wrap: wrap; gap: 4px;'>
                    {tags_html}
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown(f"<div style='font-size: 16px; font-weight: bold; color: #c62828; background-color: #ffebee; padding: 12px; border-radius: 8px; border: 1px solid #ef9a9a; margin-bottom: 20px;'>🏬 No Party Found Matching: \"{search_cust}\"</div>", unsafe_allow_html=True)

# Generate Unique Bill IDs (Smart Logic: Customer + Bill Date + Bill No)
if selected_bill_col in filtered_df.columns and 'CUSTOMERNAMEACTIVE' in filtered_df.columns:
    filtered_df['UNIQUE_BILL_ID'] = (
        filtered_df['CUSTOMERNAMEACTIVE'].astype(str).str.strip() + "_" + 
        filtered_df['BILLDATE'].dt.strftime('%Y-%m-%d') + "_" + 
        filtered_df[selected_bill_col].astype(str).str.strip()
    )
else:
    filtered_df['UNIQUE_BILL_ID'] = filtered_df['BILLDATE'].astype(str)

# Global FY Year Definition
filtered_df['FY_YEAR'] = np.where(filtered_df['BILLDATE'].dt.month < 4, filtered_df['BILLDATE'].dt.year - 1, filtered_df['BILLDATE'].dt.year)

# 🔄 DYNAMIC DATE FILTERING LOGIC
df_comp_kpi = filtered_df[(filtered_df['BILLDATE'] >= ty_start_dt) & (filtered_df['BILLDATE'] <= ty_end_dt)].copy()

if compare_mode:
    df_base_kpi = filtered_df[(filtered_df['BILLDATE'] >= ly_start_dt) & (filtered_df['BILLDATE'] <= ly_end_dt)].copy()
else:
    df_base_kpi = pd.DataFrame(columns=filtered_df.columns)

df_comp_kpi['YEAR2'] = comp_y
df_base_kpi['YEAR2'] = base_y

# Dynamic Year-to-Date isolation ranges
df_ytd_comp = df_comp_kpi.copy()
df_ytd_base = df_base_kpi.copy()
df_ytd_global = pd.concat([df_ytd_comp, df_ytd_base])

s_comp_ytd_g, s_base_ytd_g = df_ytd_comp['SALEVAL'].sum(), df_ytd_base['SALEVAL'].sum()
q_comp_ytd_g, q_base_ytd_g = df_ytd_comp['QTY'].sum(), df_ytd_base['QTY'].sum()
b_comp_ytd_g, b_base_ytd_g = df_ytd_comp['UNIQUE_BILL_ID'].nunique() if 'UNIQUE_BILL_ID' in df_ytd_comp.columns else 0, df_ytd_base['UNIQUE_BILL_ID'].nunique() if 'UNIQUE_BILL_ID' in df_ytd_base.columns else 0
d_comp_ytd_g, d_base_ytd_g = df_ytd_comp['CUSTOMERNAMEACTIVE'].nunique() if 'CUSTOMERNAMEACTIVE' in df_ytd_comp.columns else 0, df_ytd_base['CUSTOMERNAMEACTIVE'].nunique() if 'CUSTOMERNAMEACTIVE' in df_ytd_base.columns else 0

# ==========================================
# 🌟 GLOBAL PERFORMANCE AREA (STICKY FREEZE PANE)
# ==========================================
st.markdown('<div id="sticky-summary-anchor"></div>', unsafe_allow_html=True)

with st.container():
    hdr_title = f"### 🌟 Global Performance Summary ({ty_start.strftime('%d-%b-%y')} to {ty_end.strftime('%d-%b-%y')} vs LY)" if compare_mode else f"### 🌟 Global Performance Summary ({ty_start.strftime('%d-%b-%y')} to {ty_end.strftime('%d-%b-%y')})"
    st.markdown(hdr_title)

    df_comp_perf = df_comp_kpi.copy()
    df_base_perf = df_base_kpi.copy()

    s_comp = df_comp_perf['SALEVAL'].sum()
    s_base = df_base_perf['SALEVAL'].sum()
    q_comp = df_comp_perf['QTY'].sum()
    q_base = df_base_perf['QTY'].sum()
    d_comp = df_comp_perf['CUSTOMERNAMEACTIVE'].nunique() if 'CUSTOMERNAMEACTIVE' in df_comp_perf.columns else 0
    d_base = df_base_perf['CUSTOMERNAMEACTIVE'].nunique() if 'CUSTOMERNAMEACTIVE' in df_base_perf.columns else 0
    b_comp = df_comp_perf['UNIQUE_BILL_ID'].nunique() if 'UNIQUE_BILL_ID' in df_comp_perf.columns else 0
    b_base = df_base_perf['UNIQUE_BILL_ID'].nunique() if 'UNIQUE_BILL_ID' in df_base_perf.columns else 0

    abv_comp = s_comp / b_comp if b_comp > 0 else 0
    abv_base = s_base / b_base if b_base > 0 else 0
    aqv_comp = s_comp / q_comp if q_comp > 0 else 0
    aqv_base = s_base / q_base if q_base > 0 else 0
    upt_comp = q_comp / b_comp if b_comp > 0 else 0
    upt_base = q_base / b_base if b_base > 0 else 0

    if selected_disc_col:
        disc_g_c = abs(df_comp_perf[selected_disc_col].sum())
        disc_g_b = abs(df_base_perf[selected_disc_col].sum()) if compare_mode else 0
    else:
        disc_g_c, disc_g_b = 0, 0
        
    gross_g_c = abs(s_comp) + disc_g_c
    gross_g_b = abs(s_base) + disc_g_b

    disc_pct_g_c = (disc_g_c / gross_g_c * 100) if gross_g_c > 0 else 0
    disc_pct_g_b = (disc_g_b / gross_g_b * 100) if gross_g_b > 0 else 0

    # 🔥 FULL FY HISTORY CALCULATION LOGIC 
    temp_fy_all = filtered_df.copy()

    agg_funcs = {'SALEVAL': 'sum', 'QTY': 'sum'}
    if 'UNIQUE_BILL_ID' in temp_fy_all.columns:
        agg_funcs['UNIQUE_BILL_ID'] = 'nunique'
    if 'CUSTOMERNAMEACTIVE' in temp_fy_all.columns:
        agg_funcs['CUSTOMERNAMEACTIVE'] = 'nunique'
        
    fy_hist = temp_fy_all.groupby('FY_YEAR').agg(agg_funcs).sort_index(ascending=False)
    fy_hist.rename(columns={'UNIQUE_BILL_ID': 'BILLS', 'CUSTOMERNAMEACTIVE': 'DOORS'}, inplace=True)

    if 'BILLS' not in fy_hist.columns: fy_hist['BILLS'] = 0
    if 'DOORS' not in fy_hist.columns: fy_hist['DOORS'] = 0

    if selected_disc_col:
        fy_hist['DISC'] = temp_fy_all.groupby('FY_YEAR')[selected_disc_col].apply(lambda x: abs(x.sum()))
    else:
        fy_hist['DISC'] = 0

    fy_hist['SALE_LY'] = fy_hist['SALEVAL'].shift(-1)
    fy_hist['QTY_LY'] = fy_hist['QTY'].shift(-1)
    fy_hist['BILLS_LY'] = fy_hist['BILLS'].shift(-1)
    fy_hist['DOORS_LY'] = fy_hist['DOORS'].shift(-1)

    fy_hist['Sale Gr(%)'] = calc_growth_series(fy_hist['SALE_LY'], fy_hist['SALEVAL'])
    fy_hist['Qty Gr(%)'] = calc_growth_series(fy_hist['QTY_LY'], fy_hist['QTY'])
    fy_hist['Bills Gr(%)'] = calc_growth_series(fy_hist['BILLS_LY'], fy_hist['BILLS'])
    fy_hist['Doors Gr(%)'] = calc_growth_series(fy_hist['DOORS_LY'], fy_hist['DOORS'])

    fy_hist['Avg Bill Value'] = fy_hist['SALEVAL'] / fy_hist['BILLS'].replace(0, np.nan)
    fy_hist['Avg Bill Value LY'] = fy_hist['SALE_LY'] / fy_hist['BILLS_LY'].replace(0, np.nan)
    fy_hist['ABV Gr(%)'] = calc_growth_series(fy_hist['Avg Bill Value LY'], fy_hist['Avg Bill Value'])

    fy_hist['Avg Qty Value'] = fy_hist['SALEVAL'] / fy_hist['QTY'].replace(0, np.nan)
    fy_hist['Avg Qty Value LY'] = fy_hist['SALE_LY'] / fy_hist['QTY_LY'].replace(0, np.nan)
    fy_hist['AQV Gr(%)'] = calc_growth_series(fy_hist['Avg Qty Value LY'], fy_hist['Avg Qty Value'])

    fy_hist['UPT'] = fy_hist['QTY'] / fy_hist['BILLS'].replace(0, np.nan)
    fy_hist['UPT LY'] = fy_hist['QTY_LY'] / fy_hist['BILLS_LY'].replace(0, np.nan)
    fy_hist['UPT Gr(%)'] = calc_growth_series(fy_hist['UPT LY'], fy_hist['UPT'])

    fy_hist['Gross'] = fy_hist['SALEVAL'].abs() + fy_hist['DISC']
    fy_hist['Discount %'] = (fy_hist['DISC'] / fy_hist['Gross'] * 100).fillna(0)
    fy_hist['Discount % LY'] = fy_hist['Discount %'].shift(-1)
    fy_hist['Disc Gr(%)'] = fy_hist['Discount %'] - fy_hist['Discount % LY']

    sale_html, qty_html, bills_html, doors_html, disc_html, abv_html, aqv_html, upt_html = "", "", "", "", "", "", "", ""

    for fy_year, row in fy_hist.iterrows():
        fy_lbl = f"FY {str(fy_year)[-2:]}-{str(fy_year+1)[-2:]}"
        sale_html += make_fy_html(format_indian_num(row['SALEVAL'], True), row['Sale Gr(%)'], fy_lbl)
        qty_html += make_fy_html(format_indian_num(row['QTY'], False), row['Qty Gr(%)'], fy_lbl)
        bills_html += make_fy_html(format_indian_num(row['BILLS'], False), row['Bills Gr(%)'], fy_lbl)
        doors_html += make_fy_html(format_indian_num(row['DOORS'], False), row['Doors Gr(%)'], fy_lbl)
        disc_html += make_fy_html(f"{row['Discount %']:.1f}%", row['Disc Gr(%)'], fy_lbl, is_disc=True)
        abv_html += make_fy_html(format_indian_num(row['Avg Bill Value'], True), row['ABV Gr(%)'], fy_lbl)
        aqv_html += make_fy_html(format_indian_num(row['Avg Qty Value'], True), row['AQV Gr(%)'], fy_lbl)
        upt_html += make_fy_html(f"{row['UPT']:.2f}", row['UPT Gr(%)'], fy_lbl)

    r1_c1, r1_c2, r1_c3, r1_c4, r1_c5 = st.columns(5)
    r1_c1.metric(label="Total Sale", value=format_indian_num(s_comp, True), delta=f"{calc_growth(s_base, s_comp):.1f}% (LY: {format_indian_num(s_base, True)})" if compare_mode else None)
    if compare_mode: r1_c1.markdown(wrapper.format(sale_html), unsafe_allow_html=True)

    r1_c2.metric(label="Total Qty", value=format_indian_num(q_comp, False), delta=f"{calc_growth(q_base, q_comp):.1f}% (LY: {format_indian_num(q_base, False)})" if compare_mode else None)
    if compare_mode: r1_c2.markdown(wrapper.format(qty_html), unsafe_allow_html=True)

    r1_c3.metric(label="Total No Bills", value=format_indian_num(b_comp, False), delta=f"{calc_growth(b_base, b_comp):.1f}% (LY: {format_indian_num(b_base, False)})" if compare_mode else None)
    if compare_mode: r1_c3.markdown(wrapper.format(bills_html), unsafe_allow_html=True)

    r1_c4.metric(label="Total Active Doors", value=format_indian_num(d_comp, False), delta=f"{calc_growth(d_base, d_comp):.1f}% (LY: {format_indian_num(d_base, False)})" if compare_mode else None)
    if compare_mode: r1_c4.markdown(wrapper.format(doors_html), unsafe_allow_html=True)

    delta_disc_g_str = f"{(disc_pct_g_c - disc_pct_g_b):+.1f}% (LY: {disc_pct_g_b:.1f}%)" if compare_mode else None
    r1_c5.metric(label="Discount %", value=f"{disc_pct_g_c:.1f}%", delta=delta_disc_g_str, delta_color="inverse")
    if compare_mode: r1_c5.markdown(wrapper.format(disc_html), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    days_ty = max(1, (ty_end_dt - ty_start_dt).days + 1)
    days_ly = max(1, (ly_end_dt - ly_start_dt).days + 1) if compare_mode else 1
    per_day_comp = s_comp / days_ty
    per_day_base = s_base / days_ly if compare_mode else 0

    months_ty = max(1, df_comp_perf['MONTH_NAME'].nunique())
    months_ly = max(1, df_base_perf['MONTH_NAME'].nunique()) if compare_mode else 1
    per_month_comp = s_comp / months_ty
    per_month_base = s_base / months_ly if compare_mode else 0

    per_day_qty_comp = q_comp / days_ty
    per_day_qty_base = q_base / days_ly if compare_mode else 0
    per_month_qty_comp = q_comp / months_ty
    per_month_qty_base = q_base / months_ly if compare_mode else 0

    pd_qty_gr = calc_growth(per_day_qty_base, per_day_qty_comp)
    pm_qty_gr = calc_growth(per_month_qty_base, per_month_qty_comp)

    exp_month_val = per_day_comp * 30
    exp_month_qty = per_day_qty_comp * 30
    exp_year_val = per_day_comp * 365
    exp_year_qty = per_day_qty_comp * 365

    pd_qty_str = format_indian_num(per_day_qty_comp, False)
    pd_qty_gr_html = ""
    if compare_mode and not pd.isna(pd_qty_gr):
        fc = "#28a745" if pd_qty_gr >= 0 else "#dc3545"
        pd_qty_gr_html = f" (<span style='color: {fc}; font-weight:bold;'>{pd_qty_gr:+.1f}%</span>)"

    col2_html = f"<div style='font-size: 13.5px; color: #555; margin-top: 3px;'><b>Avg Qty/Day:</b> {pd_qty_str}{pd_qty_gr_html}</div>"
    col2_html += f"<div style='font-size: 13.5px; color: #555; margin-top: 12px; font-weight: bold;'>🎯 Exp. Month (30D):</div>"
    col2_html += f"<div style='font-size: 13.5px; color: #555; margin-top: 3px;'>• Value: <b style='color:#2E7D32;'>{format_indian_num(exp_month_val, True)}</b></div>"
    col2_html += f"<div style='font-size: 13.5px; color: #555; margin-top: 3px;'>• Qty: <b style='color:#1F4E79;'>{format_indian_num(exp_month_qty, False)}</b></div>"

    pm_qty_str = format_indian_num(per_month_qty_comp, False)
    pm_qty_gr_html = ""
    if compare_mode and not pd.isna(pm_qty_gr):
        fc = "#28a745" if pm_qty_gr >= 0 else "#dc3545"
        pm_qty_gr_html = f" (<span style='color: {fc}; font-weight:bold;'>{pm_qty_gr:+.1f}%</span>)"

    col3_html = f"<div style='font-size: 13.5px; color: #555; margin-top: 3px;'><b>Avg Qty/Month:</b> {pm_qty_str}{pm_qty_gr_html}</div>"
    col3_html += f"<div style='font-size: 13.5px; color: #555; margin-top: 12px; font-weight: bold;'>🎯 Exp. Year (365D):</div>"
    col3_html += f"<div style='font-size: 13.5px; color: #555; margin-top: 3px;'>• Value: <b style='color:#2E7D32;'>{format_indian_num(exp_year_val, True)}</b></div>"
    col3_html += f"<div style='font-size: 13.5px; color: #555; margin-top: 3px;'>• Qty: <b style='color:#1F4E79;'>{format_indian_num(exp_year_qty, False)}</b></div>"

    r2_c1, r2_c2, r2_c3, r2_c4, r2_c5 = st.columns(5)
    r2_c1.metric(label="Average Bill Value", value=format_indian_num(abv_comp, True), delta=f"{calc_growth(abv_base, abv_comp):.1f}% (LY: {format_indian_num(abv_base, True)})" if compare_mode else None)
    if compare_mode: r2_c1.markdown(wrapper.format(abv_html), unsafe_allow_html=True)
    r2_c2.metric(label="Per Day Avg Sale", value=format_indian_num(per_day_comp, True), delta=f"{calc_growth(per_day_base, per_day_comp):.1f}% (LY: {format_indian_num(per_day_base, True)})" if compare_mode else None)
    r2_c2.markdown(wrapper.format(col2_html), unsafe_allow_html=True)
    r2_c3.metric(label="Per Month Avg Sale", value=format_indian_num(per_month_comp, True), delta=f"{calc_growth(per_month_base, per_month_comp):.1f}% (LY: {format_indian_num(per_month_base, True)})" if compare_mode else None)
    r2_c3.markdown(wrapper.format(col3_html), unsafe_allow_html=True)
    r2_c4.metric(label="Average Qty Value", value=format_indian_num(aqv_comp, True), delta=f"{calc_growth(aqv_base, aqv_comp):.1f}% (LY: {format_indian_num(aqv_base, True)})" if compare_mode else None)
    if compare_mode: r2_c4.markdown(wrapper.format(aqv_html), unsafe_allow_html=True)
    r2_c5.metric(label="Unit Per Transaction", value=f"{upt_comp:.2f}", delta=f"{calc_growth(upt_base, upt_comp):.1f}% (LY: {upt_base:.2f})" if compare_mode else None)
    if compare_mode: r2_c5.markdown(wrapper.format(upt_html), unsafe_allow_html=True)

    # 🆕 COMPACT SEASON-WISE PERFORMANCE
    if 'SEASON' in filtered_df.columns:
        st.markdown("<br>", unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown("<div style='font-size: 16px; font-weight: bold; color: #1F4E79; margin-bottom: 10px;'>🌤️ Compact Season-wise Summary (Calendar vs Full Data)</div>", unsafe_allow_html=True)
            
            season_cal = df_comp_perf.groupby('SEASON').agg({'SALEVAL': 'sum', 'QTY': 'sum'})
            season_full = filtered_df.groupby('SEASON').agg({'SALEVAL': 'sum', 'QTY': 'sum'})
            
            all_seasons = pd.DataFrame({'SEASON': season_full.index})
            
            ss_seasons = all_seasons[all_seasons['SEASON'].str.contains('SS', na=False, case=False)].sort_values('SEASON', ascending=False).head(5)['SEASON'].tolist()
            aw_seasons = all_seasons[all_seasons['SEASON'].str.contains('AW', na=False, case=False)].sort_values('SEASON', ascending=False).head(5)['SEASON'].tolist()
            
            def render_season_row(season_list, row_title):
                if season_list:
                    st.markdown(f"<div style='font-weight: bold; color: #333; font-size: 14px; margin-top: 10px; margin-bottom: 5px;'>▶ {row_title}</div>", unsafe_allow_html=True)
                    cols = st.columns(5)
                    for i, s_name in enumerate(season_list):
                        cal_v = season_cal.loc[s_name, 'SALEVAL'] if s_name in season_cal.index else 0
                        cal_q = season_cal.loc[s_name, 'QTY'] if s_name in season_cal.index else 0
                        
                        full_v = season_full.loc[s_name, 'SALEVAL'] if s_name in season_full.index else 0
                        full_q = season_full.loc[s_name, 'QTY'] if s_name in season_full.index else 0
                        
                        if i < 5:
                            with cols[i]:
                                st.markdown(f"""
                                <div style='background-color: #f8f9fa; padding: 6px; border-radius: 5px; border: 1px solid #e0e0e0; text-align: center; margin-bottom: 10px;'>
                                    <div style='font-weight: bold; font-size: 14px; color: #d32f2f; border-bottom: 1px solid #ddd; padding-bottom: 2px; margin-bottom: 4px;'>{s_name.upper()}</div>
                                    <div style='font-size: 11px; color: #666; font-weight: bold;'>📅 Cal: <span style='color:#1F4E79;'>{format_indian_num(cal_q, False)} Qty</span> | <span style='color:#2E7D32;'>{format_indian_num(cal_v, True)}</span></div>
                                    <div style='font-size: 11px; color: #666; font-weight: bold; margin-top: 2px;'>🌍 Full: <span style='color:#1F4E79;'>{format_indian_num(full_q, False)} Qty</span> | <span style='color:#2E7D32;'>{format_indian_num(full_v, True)}</span></div>
                                </div>
                                """, unsafe_allow_html=True)

            render_season_row(ss_seasons, "SPRING/SUMMER (SS) - Top 5 Latest")
            render_season_row(aw_seasons, "AUTUMN/WINTER (AW) - Top 5 Latest")

st.markdown("<br>", unsafe_allow_html=True)
down_col1, down_col2, down_col3 = st.columns([1,2,1])
with down_col2:
    st.download_button("📥 DOWNLOAD YTD REPORT", data=to_excel(df_ytd_global), file_name="Report.xlsx", mime="application/vnd.ms-excel", use_container_width=True)

# ==========================================
# 🔥 MONTH-WISE RESTRUCTURED BREAKDOWN WITH ALL HISTORICAL YEARS INLINE
# ==========================================
st.markdown("---")
st.markdown(f"### 📅 Month-wise Analytics Breakdown")

if not df_ytd_comp.empty:
    active_months_in_data = df_ytd_comp.sort_values('BILLDATE')['MONTH_NAME'].unique().tolist()
else:
    active_months_in_data = []

if not active_months_in_data:
    st.info("No data available for the selected period.")
else:
    for m_name in active_months_in_data:
        st.markdown(f"#### 🔹 {m_name.upper()} SUMMARY")
        
        df_m_c = df_ytd_comp[df_ytd_comp['MONTH_NAME'] == m_name]
        df_m_b = df_ytd_base[df_ytd_base['MONTH_NAME'] == m_name] if compare_mode else pd.DataFrame()
        
        s_c = df_m_c['SALEVAL'].sum()
        q_c = df_m_c['QTY'].sum()
        b_c = df_m_c['UNIQUE_BILL_ID'].nunique() if 'UNIQUE_BILL_ID' in df_m_c.columns else 0
        asp_c = s_c / b_c if b_c > 0 else 0
        upt_c = q_c / b_c if b_c > 0 else 0
        
        s_b = df_m_b['SALEVAL'].sum() if not df_m_b.empty else 0
        q_b = df_m_b['QTY'].sum() if not df_m_b.empty else 0
        b_b = df_m_b['UNIQUE_BILL_ID'].nunique() if (not df_m_b.empty and 'UNIQUE_BILL_ID' in df_m_b.columns) else 0
        asp_b = s_b / b_b if b_b > 0 else 0
        upt_b = q_b / b_b if b_b > 0 else 0
        
        if selected_disc_col:
            disc_c = abs(df_m_c[selected_disc_col].sum())
            disc_b = abs(df_m_b[selected_disc_col].sum()) if (compare_mode and not df_m_b.empty) else 0
        else:
            disc_c, disc_b = 0, 0
            
        gross_c = abs(s_c) + disc_c
        gross_b = abs(s_b) + disc_b

        disc_pct_c = (disc_c / gross_c * 100) if gross_c > 0 else 0
        disc_pct_b = (disc_b / gross_b * 100) if gross_b > 0 else 0
        
        df_m_all = filtered_df[filtered_df['MONTH_NAME'] == m_name]
        m_agg = {'SALEVAL': 'sum', 'QTY': 'sum'}
        if 'UNIQUE_BILL_ID' in df_m_all.columns: m_agg['UNIQUE_BILL_ID'] = 'nunique'
            
        m_hist = df_m_all.groupby('FY_YEAR').agg(m_agg).sort_index(ascending=False)
        m_hist.rename(columns={'UNIQUE_BILL_ID': 'BILLS'}, inplace=True)
        if 'BILLS' not in m_hist.columns: m_hist['BILLS'] = 0
        
        if selected_disc_col: m_hist['DISC'] = df_m_all.groupby('FY_YEAR')[selected_disc_col].apply(lambda x: abs(x.sum()))
        else: m_hist['DISC'] = 0
            
        m_hist['SALE_LY'] = m_hist['SALEVAL'].shift(-1)
        m_hist['QTY_LY'] = m_hist['QTY'].shift(-1)
        m_hist['BILLS_LY'] = m_hist['BILLS'].shift(-1)
        
        m_hist['Sale Gr(%)'] = calc_growth_series(m_hist['SALE_LY'], m_hist['SALEVAL'])
        m_hist['Qty Gr(%)'] = calc_growth_series(m_hist['QTY_LY'], m_hist['QTY'])
        m_hist['Bills Gr(%)'] = calc_growth_series(m_hist['BILLS_LY'], m_hist['BILLS'])
        
        m_hist['ASP'] = m_hist['SALEVAL'] / m_hist['BILLS'].replace(0, np.nan)
        m_hist['ASP_LY'] = m_hist['SALE_LY'] / m_hist['BILLS_LY'].replace(0, np.nan)
        m_hist['ASP Gr(%)'] = calc_growth_series(m_hist['ASP_LY'], m_hist['ASP'])
        
        m_hist['UPT'] = m_hist['QTY'] / m_hist['BILLS'].replace(0, np.nan)
        m_hist['UPT LY'] = m_hist['QTY_LY'] / m_hist['BILLS_LY'].replace(0, np.nan)
        m_hist['UPT Gr(%)'] = calc_growth_series(m_hist['UPT LY'], m_hist['UPT'])
        
        m_hist['Gross'] = m_hist['SALEVAL'].abs() + m_hist['DISC']
        m_hist['Discount %'] = (m_hist['DISC'] / m_hist['Gross'] * 100).fillna(0)
        m_hist['Discount % LY'] = m_hist['Discount %'].shift(-1)
        m_hist['Disc Gr(%)'] = m_hist['Discount %'] - m_hist['Discount % LY']
        
        m_sale_html, m_qty_html, m_bills_html, m_asp_html, m_upt_html, m_disc_html = "", "", "", "", "", ""
        for fy_year, r_hist in m_hist.iterrows():
            fy_lbl = f"FY {str(fy_year)[-2:]}-{str(fy_year+1)[-2:]}"
            m_sale_html += make_fy_html(format_indian_num(r_hist['SALEVAL'], True), r_hist['Sale Gr(%)'], fy_lbl)
            m_qty_html += make_fy_html(format_indian_num(r_hist['QTY'], False), r_hist['Qty Gr(%)'], fy_lbl)
            m_bills_html += make_fy_html(format_indian_num(r_hist['BILLS'], False), r_hist['Bills Gr(%)'], fy_lbl)
            m_asp_html += make_fy_html(format_indian_num(r_hist['ASP'], True), r_hist['ASP Gr(%)'], fy_lbl)
            m_upt_html += make_fy_html(f"{r_hist['UPT']:.2f}", r_hist['UPT Gr(%)'], fy_lbl)
            m_disc_html += make_fy_html(f"{r_hist['Discount %']:.1f}%", r_hist['Disc Gr(%)'], fy_lbl, is_disc=True)

        with st.container(border=True):
            mc1, mc2, mc3, mc4, mc5, mc6 = st.columns(6)
            mc1.metric(label="Total Sale Value", value=format_indian_num(s_c, True), delta=f"{calc_growth(s_b, s_c):.1f}% (LY: {format_indian_num(s_b, True)})" if compare_mode else None)
            if compare_mode: mc1.markdown(wrapper.format(m_sale_html), unsafe_allow_html=True)
            mc2.metric(label="Total Sale Qty", value=format_indian_num(q_c, False), delta=f"{calc_growth(q_b, q_c):.1f}% (LY: {format_indian_num(q_b, False)})" if compare_mode else None)
            if compare_mode: mc2.markdown(wrapper.format(m_qty_html), unsafe_allow_html=True)
            mc3.metric(label="Total Bill Qty", value=format_indian_num(b_c, False), delta=f"{calc_growth(b_b, b_c):.1f}% (LY: {format_indian_num(b_b, False)})" if compare_mode else None)
            if compare_mode: mc3.markdown(wrapper.format(m_bills_html), unsafe_allow_html=True)
            mc4.metric(label="Avg Bill Value (ASP)", value=format_indian_num(asp_c, True), delta=f"{calc_growth(asp_b, asp_c):.1f}% (LY: {format_indian_num(asp_b, True)})" if compare_mode else None)
            if compare_mode: mc4.markdown(wrapper.format(m_asp_html), unsafe_allow_html=True)
            mc5.metric(label="UPT", value=f"{upt_c:.2f}", delta=f"{calc_growth(upt_b, upt_c):.1f}% (LY: {upt_b:.2f})" if compare_mode else None)
            if compare_mode: mc5.markdown(wrapper.format(m_upt_html), unsafe_allow_html=True)
            delta_disc_str = f"{(disc_pct_c - disc_pct_b):+.1f}% (LY: {disc_pct_b:.1f}%)" if compare_mode else None
            mc6.metric(label="Discount %", value=f"{disc_pct_c:.1f}%", delta=delta_disc_str, delta_color="inverse")
            if compare_mode: mc6.markdown(wrapper.format(m_disc_html), unsafe_allow_html=True)
            
            if 'CATEGORY' in df_m_c.columns:
                st.markdown("<hr style='margin: 15px 0; border: 1px dashed #e0e0e0;'>", unsafe_allow_html=True)
                st.markdown(f"<div style='font-size: 14px; font-weight: bold; color: #1F4E79; margin-bottom: 10px;'>🔝 Top 5 Categories ({m_name}) - Value & Quantity</div>", unsafe_allow_html=True)
                cat_agg_ty = df_m_c.groupby('CATEGORY').agg({'SALEVAL': 'sum', 'QTY': 'sum'})
                cat_agg_ly = df_m_b.groupby('CATEGORY').agg({'SALEVAL': 'sum', 'QTY': 'sum'}) if compare_mode and not df_m_b.empty else pd.DataFrame()
                top_cats = cat_agg_ty.sort_values(by='SALEVAL', ascending=False).head(5)
                
                if len(top_cats) > 0:
                    cat_cols = st.columns(5)
                    for i, (cat_name, row) in enumerate(top_cats.iterrows()):
                        ty_val = row['SALEVAL']
                        ty_qty = row['QTY']
                        ly_val = cat_agg_ly.loc[cat_name, 'SALEVAL'] if (compare_mode and cat_name in cat_agg_ly.index) else 0
                        ly_qty = cat_agg_ly.loc[cat_name, 'QTY'] if (compare_mode and cat_name in cat_agg_ly.index) else 0
                        delta_str_v = f"{calc_growth(ly_val, ty_val):.1f}% (LY: {format_indian_num(ly_val, True)})" if compare_mode else None
                        delta_str_q = f"{calc_growth(ly_qty, ty_qty):.1f}% (LY: {format_indian_num(ly_qty, False)})" if compare_mode else None
                        with cat_cols[i]:
                            st.metric(label=f"🛍️ {cat_name} (Val)", value=format_indian_num(ty_val, True), delta=delta_str_v)
                            st.metric(label=f"📦 {cat_name} (Qty)", value=format_indian_num(ty_qty, False), delta=delta_str_q)
            
st.markdown("---")

# ==========================================
# 📅 TABS RENDERING ROUTERS (ADMIN CONTROLLED)
# ==========================================
MASTER_TABS = [
    "📅 Selected Range Analytics Summary", "📊 Analytics Summary", "🚀 Store Growth Deep-Dive", 
    "📈 YoY Growth", "📅 Week-wise Analysis", "👕 Attributes", "👥 Customer Performance", 
    "📅 Customer Month Analysis", "🏷️ Discount & Contribution", "📊 Category vs Time", 
    "🏆 Top Performers", "📔 Mega Ledger", "🚀 Advanced Analytics"
]

visible_tabs = [t for t in MASTER_TABS if check_tab_access(t)]
if st.session_state.selected_user == "GOD (ADMIN)":
    visible_tabs.append("⚙️ Admin Control Panel")

rendered_tabs = st.tabs(visible_tabs)
tab_dict = dict(zip(visible_tabs, rendered_tabs))

def make_professional_chart(fig, title_text, is_pie=False):
    fig.update_layout(
        title={'text': title_text, 'font': {'size': 22, 'family': 'Arial', 'weight': 'bold'}, 'x': 0.02},
        font=dict(size=16, color='#333333'),
        template='plotly_white',
        margin=dict(l=10, r=220, t=85, b=45) if is_pie else dict(l=55, r=25, t=85, b=45),
        xaxis=dict(tickfont=dict(size=14), title_font=dict(size=16, weight='bold'), tickformat='.0f'),
        yaxis=dict(tickfont=dict(size=14), title_font=dict(size=16, weight='bold'), tickformat='.0f')
    )
    if is_pie:
        fig.update_layout(showlegend=True, legend=dict(font=dict(size=12), orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02))
    else:
        fig.update_layout(legend=dict(font=dict(size=13), orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        fig.update_traces(textposition='outside', textfont=dict(size=13, weight='bold'))
    return fig

def render_analytics(df_source, tab_key_prefix, is_ytd=False):
    plot_df = df_source[df_source['YEAR2'].isin([base_y, comp_y])].copy()
    
    if not plot_df.empty: m_seq = plot_df.sort_values('BILLDATE')['MONTH_NAME'].unique().tolist()
    else: m_seq = m_sequence

    if 'STATUS' in plot_df.columns:
        stat_df = plot_df[plot_df['YEAR2'] == comp_y].groupby('STATUS')['CUSTOMERNAMEACTIVE'].nunique().reset_index()
        fig_stat = px.bar(stat_df, x='STATUS', y='CUSTOMERNAMEACTIVE', color='STATUS', text_auto='.0f', color_discrete_sequence=px.colors.qualitative.Dark24)
        st.plotly_chart(make_professional_chart(fig_stat, f"1. Active Stores by Status Header ({comp_y})"), use_container_width=True, key=f"{tab_key_prefix}_status_top")
    
    cust_kpi = plot_df[plot_df['YEAR2'] == comp_y]
    cust_sum_df = cust_kpi.groupby('CUSTOMERNAMEACTIVE').agg(VALUE=('SALEVAL', 'sum'), QTY=('QTY', 'sum')).reset_index()
    s_tot = cust_sum_df['VALUE'].sum()
    
    def build_pie_mappings(df_segment):
        inside_lbls, legend_lbls = [], []
        for _, r in df_segment.iterrows():
            p_pct = (r['VALUE'] / s_tot * 100) if s_tot > 0 else 0
            v_str, q_str = format_indian_num(r['VALUE'], False), format_indian_num(r['QTY'], False)
            inside_lbls.append(f"₹{v_str}<br>{q_str} Qty<br>({p_pct:.0f}%)")
            legend_lbls.append(f"<b>{r['CUSTOMERNAMEACTIVE']}</b><br>₹{v_str} | {q_str} Qty | {p_pct:.0f}%")
        return inside_lbls, legend_lbls

    c_p1, c_p2 = st.columns(2)
    cust_top_sort = cust_sum_df.sort_values(by='VALUE', ascending=False).reset_index(drop=True)
    with c_p1:
        if not cust_top_sort.head(5).empty and s_tot > 0:
            p1_df = cust_top_sort.head(5).copy()
            in_t, leg_t = build_pie_mappings(p1_df)
            p1_df['LEGEND_TEXT'] = leg_t
            fig_p1 = px.pie(p1_df, values='VALUE', names='LEGEND_TEXT', color_discrete_sequence=px.colors.qualitative.Pastel)
            fig_p1.update_traces(text=in_t, textinfo='text', textposition='inside', textfont=dict(size=13, weight='bold'))
            st.plotly_chart(make_professional_chart(fig_p1, "2A. Top 5 High Performing Customers Share", is_pie=True), use_container_width=True, key=f"{tab_key_prefix}_p1")
    with c_p2:
        if len(cust_top_sort) > 5 and s_tot > 0:
            p2_df = cust_top_sort.iloc[5:10].copy()
            in_t, leg_t = build_pie_mappings(p2_df)
            p2_df['LEGEND_TEXT'] = leg_t
            fig_p2 = px.pie(p2_df, values='VALUE', names='LEGEND_TEXT', color_discrete_sequence=px.colors.qualitative.Set3)
            fig_p2.update_traces(text=in_t, textinfo='text', textposition='inside', textfont=dict(size=13, weight='bold'))
            st.plotly_chart(make_professional_chart(fig_p2, "2B. Rank 6-10 Performing Customers Share", is_pie=True), use_container_width=True, key=f"{tab_key_prefix}_p2")
            
    c_b1, c_b2 = st.columns(2)
    cust_bot_sort = cust_sum_df.sort_values(by='VALUE', ascending=True).reset_index(drop=True)
    
    red_palette_1 = ['#E53935', '#EF5350', '#E57373', '#EF9A9A', '#FFCDD2']
    red_palette_2 = ['#B71C1C', '#C62828', '#D32F2F', '#E53935', '#EF5350']

    with c_b1:
        if not cust_bot_sort.head(5).empty and s_tot > 0:
            b1_df = cust_bot_sort.head(5).copy()
            in_t, leg_t = build_pie_mappings(b1_df)
            b1_df['LEGEND_TEXT'] = leg_t
            fig_b1 = px.pie(b1_df, values='VALUE', names='LEGEND_TEXT', color_discrete_sequence=red_palette_1)
            fig_b1.update_traces(text=in_t, textinfo='text', textposition='inside', textfont=dict(size=13, weight='bold'))
            st.plotly_chart(make_professional_chart(fig_b1, "2C. Bottom 5 Lowest Performing Stores Share", is_pie=True), use_container_width=True, key=f"{tab_key_prefix}_b1")
    with c_b2:
        if len(cust_bot_sort) > 5 and s_tot > 0:
            b2_df = cust_bot_sort.iloc[5:10].copy()
            in_t, leg_t = build_pie_mappings(b2_df)
            b2_df['LEGEND_TEXT'] = leg_t
            fig_b2 = px.pie(b2_df, values='VALUE', names='LEGEND_TEXT', color_discrete_sequence=red_palette_2)
            fig_b2.update_traces(text=in_t, textinfo='text', textposition='inside', textfont=dict(size=13, weight='bold'))
            st.plotly_chart(make_professional_chart(fig_b2, "2D. Rank Bottom 6-10 Lowest Stores Share", is_pie=True), use_container_width=True, key=f"{tab_key_prefix}_b2")

    c_seq_v = ['#A6C8E0', '#1F4E79'] if compare_mode else ['#1F4E79']
    c_seq_q = ['#DCA6C8', '#7030A0'] if compare_mode else ['#7030A0']
    
    c_m1, c_m2 = st.columns(2)
    with c_m1:
        m_v_df = plot_df.groupby(['MONTH_NAME', 'YEAR2'])['SALEVAL'].sum().reset_index()
        m_v_df['TEXT'] = m_v_df['SALEVAL'].apply(lambda x: format_indian_num(x, True))
        fig_m_v = px.bar(m_v_df, x='MONTH_NAME', y='SALEVAL', color='YEAR2', text='TEXT', barmode='group', color_discrete_sequence=c_seq_v)
        fig_m_v.update_layout(xaxis={'categoryorder':'array', 'categoryarray': m_seq})
        st.plotly_chart(make_professional_chart(fig_m_v, "3A. Month-wise Revenue Value Trend"), use_container_width=True, key=f"{tab_key_prefix}_m_v")
    with c_m2:
        m_q_df = plot_df.groupby(['MONTH_NAME', 'YEAR2'])['QTY'].sum().reset_index()
        m_q_df['TEXT'] = m_q_df['QTY'].apply(lambda x: format_indian_num(x, False))
        fig_m_q = px.bar(m_q_df, x='MONTH_NAME', y='QTY', color='YEAR2', text='TEXT', barmode='group', color_discrete_sequence=c_seq_q)
        fig_m_q.update_layout(xaxis={'categoryorder':'array', 'categoryarray': m_seq})
        st.plotly_chart(make_professional_chart(fig_m_q, "3B. Month-wise Total Quantity Volume Trend"), use_container_width=True, key=f"{tab_key_prefix}_m_q")

    c_seq_v2 = ['#9EBD6E', '#385723'] if compare_mode else ['#385723']
    c_seq_q2 = ['#DCA6C8', '#7030A0'] if compare_mode else ['#7030A0']
    
    def render_dimension_twins(col_name, title_num):
        if col_name in plot_df.columns:
            cx1, cx2 = st.columns(2)
            with cx1:
                if col_name == 'SEASON':
                    df_v = plot_df[plot_df['YEAR2'] == comp_y].groupby(col_name)['SALEVAL'].sum().reset_index()
                    df_v['TEXT'] = df_v['SALEVAL'].apply(lambda x: format_indian_num(x, True))
                    fig_v = px.bar(df_v, x=col_name, y='SALEVAL', text='TEXT', color_discrete_sequence=['#385723'])
                else:
                    df_v = plot_df.groupby([col_name, 'YEAR2'])['SALEVAL'].sum().reset_index()
                    df_v['TEXT'] = df_v['SALEVAL'].apply(lambda x: format_indian_num(x, True))
                    fig_v = px.bar(df_v, x=col_name, y='SALEVAL', color='YEAR2', text='TEXT', barmode='group', color_discrete_sequence=c_seq_v2)
                st.plotly_chart(make_professional_chart(fig_v, f"{title_num}A. {col_name.title()} Sales Performance Value Matrix"), use_container_width=True, key=f"{tab_key_prefix}_{col_name}_v")
            with cx2:
                if col_name == 'SEASON':
                    df_q = plot_df[plot_df['YEAR2'] == comp_y].groupby(col_name)['QTY'].sum().reset_index()
                    df_q['TEXT'] = df_q['QTY'].apply(lambda x: format_indian_num(x, False))
                    fig_q = px.bar(df_q, x=col_name, y='QTY', text='TEXT', color_discrete_sequence=['#7030A0'])
                else:
                    df_q = plot_df.groupby([col_name, 'YEAR2'])['QTY'].sum().reset_index()
                    df_q['TEXT'] = df_q['QTY'].apply(lambda x: format_indian_num(x, False))
                    fig_q = px.bar(df_q, x=col_name, y='QTY', color='YEAR2', text='TEXT', barmode='group', color_discrete_sequence=c_seq_q2)
                st.plotly_chart(make_professional_chart(fig_q, f"{title_num}B. {col_name.title()} Volume Quantity Matrix"), use_container_width=True, key=f"{tab_key_prefix}_{col_name}_q")

    render_dimension_twins('CATEGORY', 4)
    render_dimension_twins('STATE', 5)
    render_dimension_twins('MANAGER', 6)
    render_dimension_twins('FIT', 7)
    render_dimension_twins('SEASON', 8)
    render_dimension_twins('EOSS/FRESH', 9)
    render_dimension_twins('FORMAL/CASUAL', 10)


# ==========================================
# 📌 TAB CONTENTS RENDERING
# ==========================================
if "📅 Selected Range Analytics Summary" in tab_dict:
    with tab_dict["📅 Selected Range Analytics Summary"]:
        st.markdown(f"#### 📢 **PLEASE NOTE: This data is filtered based on Selected Date Range**")
        if df_ytd_global.empty: st.warning("Selected range records empty.")
        else: render_analytics(df_ytd_global, "ytd", True)

if "📊 Analytics Summary" in tab_dict:
    with tab_dict["📊 Analytics Summary"]:
        st.subheader("Visual Analytics Overview")
        render_analytics(pd.concat([df_comp_kpi, df_base_kpi]), "full", False)

if "🚀 Store Growth Deep-Dive" in tab_dict:
    with tab_dict["🚀 Store Growth Deep-Dive"]:
        if not compare_mode:
            st.info("⚠️ YoY Growth Analytics tab is disabled because **Comparison Mode** is OFF. Please enable it from the sidebar to view these insights.")
        else:
            st.markdown("### 💰 1. Value Wise Growth Performance Summary")
            df_sg_val = pd.concat([df_comp_kpi, df_base_kpi]).pivot_table(index='CUSTOMERNAMEACTIVE', columns='YEAR2', values='SALEVAL', aggfunc='sum', fill_value=0).reset_index()
            if base_y in df_sg_val.columns and comp_y in df_sg_val.columns:
                df_sg_val['GROWTH_PCT'] = calc_growth_series(df_sg_val[base_y], df_sg_val[comp_y]).round(0)
                df_sg_val = df_sg_val.replace([np.inf, -np.inf], np.nan).dropna(subset=['GROWTH_PCT'])
                df_pos_val = df_sg_val[df_sg_val['GROWTH_PCT'] >= 0].sort_values(by='GROWTH_PCT', ascending=False)
                df_neg_val = df_sg_val[df_sg_val['GROWTH_PCT'] < 0].sort_values(by='GROWTH_PCT', ascending=True)
                
                v_col1, v_col2 = st.columns(2)
                with v_col1:
                    f_top_v = px.bar(df_pos_val.head(5), x='CUSTOMERNAMEACTIVE', y='GROWTH_PCT', title="Top 5 Growth % Stores (Value)", color_discrete_sequence=['#2E7D32'])
                    f_top_v.update_traces(texttemplate='%{y:+.0f}%', textposition='outside')
                    st.plotly_chart(make_professional_chart(f_top_v, "Top 5 Growth (Value)"), use_container_width=True, key="growth_val_1")
                with v_col2:
                    f_rnk_v = px.bar(df_pos_val.iloc[5:10], x='CUSTOMERNAMEACTIVE', y='GROWTH_PCT', title="Rank 6-10 Growth % Stores (Value)", color_discrete_sequence=['#81C784'])
                    f_rnk_v.update_traces(texttemplate='%{y:+.0f}%', textposition='outside')
                    st.plotly_chart(make_professional_chart(f_rnk_v, "Rank 6-10 Growth (Value)"), use_container_width=True, key="growth_val_2")
                    
                v_col3, v_col4 = st.columns(2)
                with v_col3:
                    fig_all_v_pos = px.bar(df_pos_val, x='CUSTOMERNAMEACTIVE', y='GROWTH_PCT', title="All Growing Stores (Value)", color_discrete_sequence=['#4CAF50'])
                    fig_all_v_pos.update_traces(texttemplate='%{y:+.0f}%', textposition='outside')
                    fig_all_v_pos.update_layout(xaxis=dict(tickmode='linear', dtick=1, tickangle=-45), height=550)
                    st.plotly_chart(make_professional_chart(fig_all_v_pos, "All Growing Stores (Value)"), use_container_width=True, key="growth_val_3")
                with v_col4:
                    fig_all_v_neg = px.bar(df_neg_val, x='CUSTOMERNAMEACTIVE', y='GROWTH_PCT', title="All Degrowing Stores (Value)", color_discrete_sequence=['#D32F2F'])
                    fig_all_v_neg.update_traces(texttemplate='%{y:.0f}%', textposition='outside')
                    fig_all_v_neg.update_layout(xaxis=dict(tickmode='linear', dtick=1, tickangle=-45), height=550)
                    st.plotly_chart(make_professional_chart(fig_all_v_neg, "All Degrowing Stores (Value)"), use_container_width=True, key="growth_val_4")

            st.markdown("---")
            st.markdown("### 👕 2. Quantity Wise Growth Performance Summary")
            df_sg_qty = pd.concat([df_comp_kpi, df_base_kpi]).pivot_table(index='CUSTOMERNAMEACTIVE', columns='YEAR2', values='QTY', aggfunc='sum', fill_value=0).reset_index()
            if base_y in df_sg_qty.columns and comp_y in df_sg_qty.columns:
                df_sg_qty['GROWTH_PCT'] = calc_growth_series(df_sg_qty[base_y], df_sg_qty[comp_y]).round(0)
                df_sg_qty = df_sg_qty.replace([np.inf, -np.inf], np.nan).dropna(subset=['GROWTH_PCT'])
                df_pos_qty = df_sg_qty[df_sg_qty['GROWTH_PCT'] >= 0].sort_values(by='GROWTH_PCT', ascending=False)
                df_neg_qty = df_sg_qty[df_sg_qty['GROWTH_PCT'] < 0].sort_values(by='GROWTH_PCT', ascending=True)
                
                q_col1, q_col2 = st.columns(2)
                with q_col1:
                    f_top_q = px.bar(df_pos_qty.head(5), x='CUSTOMERNAMEACTIVE', y='GROWTH_PCT', title="Top 5 Growth % Stores (Qty)", color_discrete_sequence=['#1565C0'])
                    f_top_q.update_traces(texttemplate='%{y:+.0f}%', textposition='outside')
                    st.plotly_chart(make_professional_chart(f_top_q, "Top 5 Growth (Qty)"), use_container_width=True, key="growth_qty_1")
                with q_col2:
                    f_rnk_q = px.bar(df_pos_qty.iloc[5:10], x='CUSTOMERNAMEACTIVE', y='GROWTH_PCT', title="Rank 6-10 Growth % Stores (Qty)", color_discrete_sequence=['#64B5F6'])
                    f_rnk_q.update_traces(texttemplate='%{y:+.0f}%', textposition='outside')
                    st.plotly_chart(make_professional_chart(f_rnk_q, "Rank 6-10 Growth (Qty)"), use_container_width=True, key="growth_qty_2")
                    
                q_col3, q_col4 = st.columns(2)
                with q_col3:
                    fig_all_q_pos = px.bar(df_pos_val, x='CUSTOMERNAMEACTIVE', y='GROWTH_PCT', title="All Growing Stores (Qty)", color_discrete_sequence=['#2196F3'])
                    fig_all_q_pos.update_traces(texttemplate='%{y:+.0f}%', textposition='outside')
                    fig_all_q_pos.update_layout(xaxis=dict(tickmode='linear', dtick=1, tickangle=-45), height=550)
                    st.plotly_chart(make_professional_chart(fig_all_q_pos, "All Growing Stores (Qty)"), use_container_width=True, key="growth_qty_3")
                with q_col4:
                    fig_all_q_neg = px.bar(df_neg_qty, x='CUSTOMERNAMEACTIVE', y='GROWTH_PCT', title="All Degrowing Stores (Qty)", color_discrete_sequence=['#E53935'])
                    fig_all_q_neg.update_traces(texttemplate='%{y:.0f}%', textposition='outside')
                    fig_all_q_neg.update_layout(xaxis=dict(tickmode='linear', dtick=1, tickangle=-45), height=550)
                    st.plotly_chart(make_professional_chart(fig_all_q_neg, "All Degrowing Stores (Qty)"), use_container_width=True, key="growth_qty_4")

if "📈 YoY Growth" in tab_dict:
    with tab_dict["📈 YoY Growth"]:
        st.subheader("Time-wise Ledger Comparison" if compare_mode else "Time-wise Ledger Summary")
        view = st.radio("Group By:", ["Day-wise", "Month-wise", "Quarter-wise", "Year-wise"], horizontal=True)
        df_yo = pd.concat([df_comp_kpi, df_base_kpi]).copy()
        
        start_month_num = ty_start_dt.month
        df_yo['F_Month'] = (df_yo['BILLDATE'].dt.month - start_month_num) % 12 + 1

        if view == "Year-wise":
            agg = df_yo.groupby('YEAR2')[['SALEVAL', 'QTY']].sum()
            b_s = float(agg.loc[base_y, 'SALEVAL']) if base_y in agg.index else 0.0
            c_s = float(agg.loc[comp_y, 'SALEVAL']) if comp_y in agg.index else 0.0
            b_q = float(agg.loc[base_y, 'QTY']) if base_y in agg.index else 0.0
            c_q = float(agg.loc[comp_y, 'QTY']) if comp_y in agg.index else 0.0
            final_df = pd.DataFrame({
                'Period': [f"{base_y} vs {comp_y}" if compare_mode else f"{comp_y}"],
                f'Sale {base_y}': [b_s], f'Sale {comp_y}': [c_s],
                'Sale Gr(%)': [calc_growth(b_s, c_s)],
                f'Qty {base_y}': [b_q], f'Qty {comp_y}': [c_q],
                'Qty Gr(%)': [calc_growth(b_q, c_q)]
            })
        else:
            if view == "Day-wise":
                df_yo['Sort'] = df_yo['F_Month'] * 100 + df_yo['BILLDATE'].dt.day
                df_yo['Period'] = df_yo['BILLDATE'].dt.strftime('%d-%b')
            elif view == "Month-wise":
                df_yo['Sort'] = df_yo['F_Month']
                df_yo['Period'] = df_yo['BILLDATE'].dt.strftime('%b')
            else:
                df_yo['Sort'] = (df_yo['F_Month'] - 1) // 3 + 1
                df_yo['Period'] = "Q" + df_yo['Sort'].astype(str)

            p_sale = df_yo.pivot_table(index=['Sort', 'Period'], columns='YEAR2', values='SALEVAL', aggfunc='sum', fill_value=0)
            p_qty = df_yo.pivot_table(index=['Sort', 'Period'], columns='YEAR2', values='QTY', aggfunc='sum', fill_value=0)

            for y in [base_y, comp_y]:
                if y not in p_sale.columns: p_sale[y] = 0
                if y not in p_qty.columns: p_qty[y] = 0

            p_sale['LY_S_L'] = p_sale[base_y].cumsum(); p_sale['TY_S_L'] = p_sale[comp_y].cumsum()
            p_qty['LY_Q_L'] = p_qty[base_y].cumsum(); p_qty['TY_Q_L'] = p_qty[comp_y].cumsum()

            final_df = pd.DataFrame({
                f'Sale {base_y}': p_sale[base_y], f'Sale {comp_y}': p_sale[comp_y],
                'Sale Gr(%)': calc_growth_series(p_sale[base_y], p_sale[comp_y]),
                'LY Sale Ledger': p_sale['LY_S_L'], 'TY Sale Ledger': p_sale['TY_S_L'],
                'Sale Ledger Gr(%)': calc_growth_series(p_sale['LY_S_L'], p_sale['TY_S_L']),
                f'Qty {base_y}': p_qty[base_y], f'Qty {comp_y}': p_qty[comp_y], 
                'Qty Gr(%)': calc_growth_series(p_qty[base_y], p_qty[comp_y]),
                'LY Qty Ledger': p_qty['LY_Q_L'], 'TY Qty Ledger': p_qty['TY_Q_L'],
                'Qty Ledger Gr(%)': calc_growth_series(p_qty['LY_Q_L'], p_qty[comp_y])
            })

            if view == "Day-wise":
                month_ranges_dict = {'Jan': '1 JAN - 31 JAN', 'Feb': '1 FEB - 28/29/30 FEB', 'Mar': '1 MAR - 31 MAR', 'Apr': '1 APR - 30 APR', 'May': '1 MAY - 31 MAY', 'Jun': '1 JUN - 30 JUN', 'Jul': '1 JUL - 31 JUL', 'Aug': '1 AUG - 31 AUG', 'Sep': '1 SEP - 30 SEP', 'Oct': '1 OCT - 31 OCT', 'Nov': '1 NOV - 30 NOV', 'Dec': '1 DEC - 31 DEC'}
                f_month = final_df.index.get_level_values('Sort') // 100
                
                final_df['LY MTD Sale Ledger'] = final_df[f'Sale {base_y}'].groupby(f_month).cumsum()
                final_df['TY MTD Sale Ledger'] = final_df[f'Sale {comp_y}'].groupby(f_month).cumsum()
                final_df['MTD Sale Ledger Gr(%)'] = calc_growth_series(final_df['LY MTD Sale Ledger'], final_df['TY MTD Sale Ledger'])
                final_df['LY MTD Qty Ledger'] = final_df[f'Qty {base_y}'].groupby(f_month).cumsum()
                final_df['TY MTD Qty Ledger'] = final_df[f'Qty {comp_y}'].groupby(f_month).cumsum()
                final_df['MTD Qty Ledger Gr(%)'] = calc_growth_series(final_df['LY MTD Qty Ledger'], final_df['TY MTD Qty Ledger'])
                
                total_row = final_df.sum(numeric_only=True).to_frame().T
                total_row.index = pd.MultiIndex.from_tuples([(99999, "GRAND TOTAL")], names=['Sort', 'Period'])
                total_row['Sale Gr(%)'] = calc_growth(total_row[f'Sale {base_y}'].iloc[0], total_row[f'Sale {comp_y}'].iloc[0])
                total_row['Qty Gr(%)'] = calc_growth(total_row[f'Qty {base_y}'].iloc[0], total_row[f'Qty {comp_y}'].iloc[0])
                
                ledgers_cols = ['LY Sale Ledger', 'TY Sale Ledger', 'Sale Ledger Gr(%)', 'LY Qty Ledger', 'TY Qty Ledger', 'Qty Ledger Gr(%)', 'LY MTD Sale Ledger', 'TY MTD Sale Ledger', 'MTD Sale Ledger Gr(%)', 'LY MTD Qty Ledger', 'TY MTD Qty Ledger', 'MTD Qty Ledger Gr(%)']
                total_row[ledgers_cols] = "-"
                chunks = []
                for month, group in final_df.groupby(f_month):
                    month_total = group.sum(numeric_only=True).to_frame().T
                    month_name = group.index.get_level_values('Period')[0].split('-')[1]
                    range_text = month_ranges_dict.get(month_name, "")
                    period_label = f"⭐ {month_name.upper()} TOTAL ({range_text})" if range_text else f"⭐ {month_name.upper()} TOTAL"
                    month_total.index = pd.MultiIndex.from_tuples([(month * 100 + 99, period_label)], names=['Sort', 'Period'])
                    month_total['Sale Gr(%)'] = calc_growth(month_total[f'Sale {base_y}'].iloc[0], month_total[f'Sale {comp_y}'].iloc[0])
                    month_total['Qty Gr(%)'] = calc_growth(month_total[f'Qty {base_y}'].iloc[0], month_total[f'Qty {comp_y}'].iloc[0])
                    month_total[ledgers_cols] = "-"
                    chunks.append(group)
                    chunks.append(month_total)
                chunks.append(total_row)
                final_df = pd.concat(chunks).sort_index(level='Sort')

            final_df = final_df.droplevel('Sort').reset_index().rename(columns={'index': 'Period'})
            
            if view == "Day-wise":
                sale_cols = [f'Sale {base_y}', f'Sale {comp_y}', 'Sale Gr(%)', 'LY MTD Sale Ledger', 'TY MTD Sale Ledger', 'MTD Sale Ledger Gr(%)', 'LY Sale Ledger', 'TY Sale Ledger', 'Sale Ledger Gr(%)']
                qty_cols = [f'Qty {base_y}', f'Qty {comp_y}', 'Qty Gr(%)', 'LY MTD Qty Ledger', 'TY MTD Qty Ledger', 'MTD Qty Ledger Gr(%)', 'LY Qty Ledger', 'TY Qty Ledger', 'Qty Ledger Gr(%)']
                final_df = final_df[['Period'] + [c for c in sale_cols if c in final_df.columns] + [c for c in qty_cols if c in final_df.columns]]
            else:
                sale_cols = [c for c in final_df.columns if c != 'Period' and 'QTY' not in c.upper()]
                qty_cols = [c for c in final_df.columns if 'QTY' in c.upper()]
                final_df = final_df[['Period'] + sale_cols + qty_cols]

        if not compare_mode:
            final_df = clean_df_for_single_mode(final_df, base_y)
            
        for col in final_df.columns:
            if col != 'Period':
                final_df[col] = final_df[col].map(lambda x: format_cell(x, col))

        st.dataframe(style_dataframe(final_df), use_container_width=True)

if "📅 Week-wise Analysis" in tab_dict:
    with tab_dict["📅 Week-wise Analysis"]:
        st.subheader("📅 Complete Week Analysis Matrix Layout")
        df_wk = pd.concat([df_comp_kpi, df_base_kpi]).copy()
        
        if not df_wk.empty:
            df_wk['FY_START_YEAR'] = np.where(df_wk['BILLDATE'].dt.month < 4, df_wk['BILLDATE'].dt.year - 1, df_wk['BILLDATE'].dt.year)
            df_wk['FY_START_DATE'] = pd.to_datetime(df_wk['FY_START_YEAR'].astype(str) + '-04-01')
            df_wk['DAYS_SINCE_FY'] = (df_wk['BILLDATE'] - df_wk['FY_START_DATE']).dt.days
            df_wk['WEEK_NUM'] = (df_wk['DAYS_SINCE_FY'] // 7) + 1
            df_wk['DAY_NAME'] = df_wk['BILLDATE'].dt.strftime('%a').str.upper()
            
            w_opt_col1, w_opt_col2, w_opt_col3 = st.columns(3)
            weeks_avail = sorted(df_wk['WEEK_NUM'].unique())
            sel_wk = w_opt_col1.selectbox("Select Target Week:", weeks_avail, format_func=lambda x: f"WK-{x:02d}")
            
            metric_mode = w_opt_col2.radio("Select View Metric Mapping:", ["Sale Value (₹)", "Quantity (Qty)"], horizontal=True)
            target_wk_col = 'SALEVAL' if "Sale Value" in metric_mode else 'QTY'
            is_curr = True if "Sale Value" in metric_mode else False
            
            dim_mode = w_opt_col3.radio("Select Segment Dimension Layer:", ["Customer-wise", "Manager-wise"], horizontal=True)
            target_wk_index = 'CUSTOMERNAMEACTIVE' if "Customer-wise" in dim_mode else 'MANAGER'
            
            df_target_wk = df_wk[df_wk['WEEK_NUM'] == sel_wk]
            
            if target_wk_index in df_target_wk.columns:
                piv_wk = df_target_wk.pivot_table(index=target_wk_index, columns=['YEAR2', 'DAY_NAME'], values=target_wk_col, aggfunc='sum', fill_value=0)
                
                days_seq = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']
                matrix_rows = []
                
                for segment in piv_wk.index:
                    row_data = {'Name': segment}
                    ly_ttl = 0
                    for d in days_seq:
                        val = piv_wk.loc[segment, (base_y, d)] if (base_y, d) in piv_wk.columns else 0
                        row_data[f'LY_{d}'] = val
                        ly_ttl += val
                    row_data['LY_TTL'] = ly_ttl
                    
                    ty_ttl = 0
                    for d in days_seq:
                        val = piv_wk.loc[segment, (comp_y, d)] if (comp_y, d) in piv_wk.columns else 0
                        row_data[f'TY_{d}'] = val
                        ty_ttl += val
                    row_data['TY_TTL'] = ty_ttl
                    
                    for d in days_seq:
                        row_data[f'GR_{d}'] = calc_growth(row_data[f'LY_{d}'], row_data[f'TY_{d}'])
                    row_data['GR_TTL'] = calc_growth(ly_ttl, ty_ttl)
                    
                    matrix_rows.append(row_data)
                    
                if matrix_rows:
                    f_wk_df = pd.DataFrame(matrix_rows)
                    t_sum = f_wk_df.sum(numeric_only=True)
                    g_row = {'Name': 'G TOTAL'}
                    for d in days_seq + ['TTL']:
                        g_row[f'LY_{d}'] = t_sum.get(f'LY_{d}', 0)
                        g_row[f'TY_{d}'] = t_sum.get(f'TY_{d}', 0)
                        g_row[f'GR_{d}'] = calc_growth(g_row[f'LY_{d}'], g_row[f'TY_{d}'])
                    f_wk_df = pd.concat([f_wk_df, pd.DataFrame([g_row])]).reset_index(drop=True)
                    
                    disp_cols = ['Name']
                    for d in days_seq + ['TTL']: 
                        if compare_mode: disp_cols.append(f'LY_{d}')
                        disp_cols.append(f'TY_{d}')
                        if compare_mode: disp_cols.append(f'GR_{d}')
                    f_wk_df = f_wk_df[disp_cols]
                    
                    for col in f_wk_df.columns:
                        if col == 'Name': continue
                        if 'GR_' in col:
                            f_wk_df[col] = f_wk_df[col].map(lambda x: "➖ 0%" if x==0 else (f"🔺 {x:.0f}%" if x>0 else f"🔻 {abs(x):.0f}%") if not pd.isna(x) else "N/A")
                        elif 'LY_' in col or 'TY_' in col:
                            f_wk_df[col] = f_wk_df[col].map(lambda x: format_indian_num(x, is_curr))
                            
                    st.dataframe(style_dataframe(f_wk_df), use_container_width=True)
            else:
                st.info("Selected week counts template range is clear.")
        else:
            st.info("Week data sync process active.")

if "👕 Attributes" in tab_dict:
    with tab_dict["👕 Attributes"]:
        st.subheader("Attributes Deep-Dive")
        possible_attributes = ['CATEGORY', 'MANAGER', 'CUSTOMERNAMEACTIVE', 'STATE', 'STATUS', 'SIZE', 'SEASON', 'FIT', 'EOSS/FRESH', 'FORMAL/CASUAL']
        available_attributes = [attr for attr in possible_attributes if attr in sheet_data.columns]
        
        if not available_attributes:
            st.warning("⚠️ Column names check karein.")
        else:
            selected_attr = st.selectbox("📌 Select Dimension:", available_attributes)
            df_attr = pd.concat([df_comp_kpi, df_base_kpi]).copy()
            p_sale_attr = df_attr.pivot_table(index=selected_attr, columns='YEAR2', values='SALEVAL', aggfunc='sum', fill_value=0)
            p_qty_attr = df_attr.pivot_table(index=selected_attr, columns='YEAR2', values='QTY', aggfunc='sum', fill_value=0)
            for y in [base_y, comp_y]:
                if y not in p_sale_attr.columns: p_sale_attr[y] = 0
                if y not in p_qty_attr.columns: p_qty_attr[y] = 0
            attr_df = pd.DataFrame({
                selected_attr: p_sale_attr.index,
                f'Sale {base_y}': p_sale_attr[base_y],
                f'Sale {comp_y}': p_sale_attr[comp_y],
                'Sale Gr(%)': calc_growth_series(p_sale_attr[base_y], p_sale_attr[comp_y]),
                f'Qty {base_y}': p_qty_attr[base_y],
                f'Qty {comp_y}': p_qty_attr[comp_y],
                'Qty Gr(%)': calc_growth_series(p_qty_attr[base_y], p_qty_attr[comp_y])
            })
            attr_df = attr_df.sort_values(by=f'Sale {comp_y}', ascending=False)
            if not attr_df.empty:
                total_row_attr = attr_df.sum(numeric_only=True).to_frame().T
                total_row_attr.index = ["GRAND TOTAL"]
                total_row_attr['Sale Gr(%)'] = calc_growth(total_row_attr[f'Sale {base_y}'].iloc[0], total_row_attr[f'Sale {comp_y}'].iloc[0])
                total_row_attr['Qty Gr(%)'] = calc_growth(total_row_attr[f'Qty {base_y}'].iloc[0], total_row_attr[f'Qty {comp_y}'].iloc[0])
                attr_df = pd.concat([attr_df, total_row_attr])
            
            sale_cols = [c for c in attr_df.columns if c != selected_attr and 'QTY' not in c.upper()]
            qty_cols = [c for c in attr_df.columns if 'QTY' in c.upper()]
            attr_df = attr_df[[selected_attr] + sale_cols + qty_cols]
            
            if not compare_mode:
                attr_df = clean_df_for_single_mode(attr_df, base_y)
                
            for col in attr_df.columns:
                if col != selected_attr:
                    attr_df[col] = attr_df[col].map(lambda x: format_cell(x, col))
            st.dataframe(style_dataframe(attr_df), use_container_width=True)

if "👥 Customer Performance" in tab_dict:
    with tab_dict["👥 Customer Performance"]:
        st.subheader("Customer-wise Performance Metrics")
        df_c = pd.concat([df_comp_kpi, df_base_kpi]).copy()
        
        if not df_c.empty and 'CUSTOMERNAMEACTIVE' in df_c.columns and 'UNIQUE_BILL_ID' in df_c.columns:
            cust_raw = df_c.groupby(['CUSTOMERNAMEACTIVE', 'YEAR2']).agg(SALE=('SALEVAL', 'sum'), QTY=('QTY', 'sum'), BILLS=('UNIQUE_BILL_ID', 'nunique')).unstack(fill_value=0)
                
            for y in [base_y, comp_y]:
                if ('SALE', y) not in cust_raw.columns: cust_raw[('SALE', y)] = 0
                if ('QTY', y) not in cust_raw.columns: cust_raw[('QTY', y)] = 0
                if ('BILLS', y) not in cust_raw.columns: cust_raw[('BILLS', y)] = 0
                
            c_df = pd.DataFrame(index=cust_raw.index)
            c_df['CUSTOMERNAMEACTIVE'] = cust_raw.index
            c_df[f'Sale {base_y}'] = cust_raw[('SALE', base_y)]
            c_df[f'Sale {comp_y}'] = cust_raw[('SALE', comp_y)] if ('SALE', comp_y) in cust_raw.columns else 0
            c_df['Sale Gr(%)'] = calc_growth_series(c_df[f'Sale {base_y}'], c_df[f'Sale {comp_y}'])
            c_df[f'Qty {base_y}'] = cust_raw[('QTY', base_y)]
            c_df[f'Qty {comp_y}'] = cust_raw[('QTY', comp_y)]
            c_df['Qty Gr(%)'] = calc_growth_series(c_df[f'Qty {base_y}'], c_df[f'Qty {comp_y}'])
            c_df[f'Bills {base_y}'] = cust_raw[('BILLS', base_y)]
            c_df[f'Bills {comp_y}'] = cust_raw[('BILLS', comp_y)]
            c_df['BILLS Gr(%)'] = calc_growth_series(c_df[f'Bills {base_y}'], c_df[f'Bills {comp_y}'])
            
            c_df[f'Avg Bill Val {base_y}'] = c_df[f'Sale {base_y}'] / c_df[f'Bills {base_y}'].replace(0, np.nan)
            c_df[f'Avg Bill Val {comp_y}'] = c_df[f'Sale {comp_y}'] / c_df[f'Bills {comp_y}'].replace(0, np.nan)
            c_df['Avg Bill Val Gr(%)'] = calc_growth_series(c_df[f'Avg Bill Val {base_y}'], c_df[f'Avg Bill Val {comp_y}'])
            c_df[f'Avg Qty Val {base_y}'] = c_df[f'Sale {base_y}'] / c_df[f'Qty {base_y}'].replace(0, np.nan)
            c_df[f'Avg Qty Val {comp_y}'] = c_df[f'Sale {comp_y}'] / c_df[f'Qty {comp_y}'].replace(0, np.nan)
            c_df['Avg Qty Val Gr(%)'] = calc_growth_series(c_df[f'Avg Qty Val {base_y}'], c_df[f'Avg Qty Val {comp_y}'])
            
            c_df[f'UPT {base_y}'] = c_df[f'Qty {base_y}'] / c_df[f'Bills {base_y}'].replace(0, np.nan)
            c_df[f'UPT {comp_y}'] = c_df[f'Qty {comp_y}'] / c_df[f'Bills {comp_y}'].replace(0, np.nan)
            c_df['UPT Gr(%)'] = calc_growth_series(c_df[f'UPT {base_y}'], c_df[f'UPT {comp_y}'])
            
            full_cust_raw = filtered_df.pivot_table(index='CUSTOMERNAMEACTIVE', columns='FY_YEAR', values=['SALEVAL', 'QTY'], aggfunc='sum', fill_value=0)
            
            full_sale_cols = []
            full_qty_cols = []
            
            if not full_cust_raw.empty:
                for metric, year in full_cust_raw.columns:
                    if metric == "SALEVAL":
                        fy_label = f"FY {str(year)[-2:]}-{str(year+1)[-2:]} Full Sale"
                        c_df[fy_label] = full_cust_raw[(metric, year)]
                        full_sale_cols.append(fy_label)
                    elif metric == "QTY":
                        fy_label = f"FY {str(year)[-2:]}-{str(year+1)[-2:]} Full Qty"
                        c_df[fy_label] = full_cust_raw[(metric, year)]
                        full_qty_cols.append(fy_label)
            
            c_df.index.name = None
            c_df = c_df.fillna(0).sort_values(by='CUSTOMERNAMEACTIVE', ascending=True).reset_index(drop=True)
            
            if not c_df.empty:
                t_row = c_df.sum(numeric_only=True).to_frame().T
                t_row['CUSTOMERNAMEACTIVE'] = "GRAND TOTAL"
                t_row['Sale Gr(%)'] = calc_growth(t_row[f'Sale {base_y}'].iloc[0], t_row[f'Sale {comp_y}'].iloc[0])
                t_row['Qty Gr(%)'] = calc_growth(t_row[f'Qty {base_y}'].iloc[0], t_row[f'Qty {comp_y}'].iloc[0])
                t_row['BILLS Gr(%)'] = calc_growth(t_row[f'Bills {base_y}'].iloc[0], t_row[f'Bills {comp_y}'].iloc[0])
                t_row[f'Avg Bill Val {base_y}'] = t_row[f'Sale {base_y}'].iloc[0] / t_row[f'Bills {base_y}'].iloc[0] if t_row[f'Bills {base_y}'].iloc[0] > 0 else 0
                t_row[f'Avg Bill Val {comp_y}'] = t_row[f'Sale {comp_y}'].iloc[0] / t_row[f'Bills {comp_y}'].iloc[0] if t_row[f'Bills {comp_y}'].iloc[0] > 0 else 0
                t_row['Avg Bill Val Gr(%)'] = calc_growth(t_row[f'Avg Bill Val {base_y}'].iloc[0], t_row[f'Avg Bill Val {comp_y}'].iloc[0])
                t_row[f'Avg Qty Val {base_y}'] = t_row[f'Sale {base_y}'].iloc[0] / t_row[f'Qty {base_y}'].iloc[0] if t_row[f'Qty {base_y}'].iloc[0] > 0 else 0
                t_row[f'Avg Qty Val {comp_y}'] = t_row[f'Sale {comp_y}'].iloc[0] / t_row[f'Qty {comp_y}'].iloc[0] if t_row[f'Qty {comp_y}'].iloc[0] > 0 else 0
                t_row['Avg Qty Val Gr(%)'] = calc_growth(t_row[f'Avg Qty Val {base_y}'].iloc[0], t_row[f'Avg Qty Val {comp_y}'].iloc[0])
                t_row[f'UPT {base_y}'] = t_row[f'Qty {base_y}'].iloc[0] / t_row[f'Bills {base_y}'].iloc[0] if t_row[f'Bills {base_y}'].iloc[0] > 0 else 0
                t_row[f'UPT {comp_y}'] = t_row[f'Qty {comp_y}'].iloc[0] / t_row[f'Bills {comp_y}'].iloc[0] if t_row[f'Bills {comp_y}'].iloc[0] > 0 else 0
                t_row['UPT Gr(%)'] = calc_growth(t_row[f'UPT {base_y}'].iloc[0], t_row[f'UPT {comp_y}'].iloc[0])
                c_df = pd.concat([t_row, c_df], ignore_index=True)
                
            full_sale_cols = sorted(full_sale_cols, reverse=True)
            full_qty_cols = sorted(full_qty_cols, reverse=True)
            
            c_cols_order = [
                'CUSTOMERNAMEACTIVE',
                f'Sale {base_y}', f'Sale {comp_y}', 'Sale Gr(%)'
            ] + full_sale_cols + [
                f'Qty {base_y}', f'Qty {comp_y}', 'Qty Gr(%)'
            ] + full_qty_cols + [
                f'Bills {base_y}', f'Bills {comp_y}', 'BILLS Gr(%)',
                f'Avg Bill Val {base_y}', f'Avg Bill Val {comp_y}', 'Avg Bill Val Gr(%)',
                f'Avg Qty Val {base_y}', f'Avg Qty Val {comp_y}', 'Avg Qty Val Gr(%)',
                f'UPT {base_y}', f'UPT {comp_y}', 'UPT Gr(%)'
            ]
            
            c_cols_order = [c for c in c_cols_order if c in c_df.columns]
            c_df = c_df[c_cols_order]
            
            if not compare_mode:
                c_df = clean_df_for_single_mode(c_df, base_y)
                
            for col in c_df.columns:
                if col != 'CUSTOMERNAMEACTIVE':
                    if 'Gr(%)' in col or 'GR(%)' in col.upper(): c_df[col] = c_df[col].map(lambda x: format_cell(x, col))
                    elif 'Sale' in col or 'Val' in col: c_df[col] = c_df[col].map(lambda x: format_indian_num(x, True))
                    elif 'UPT' in col: c_df[col] = c_df[col].map(lambda x: f"{x:.2f}")
                    else: c_df[col] = c_df[col].map(lambda x: format_indian_num(x, False))
                    
            st.dataframe(style_dataframe(c_df), use_container_width=True, hide_index=True)

if "📅 Customer Month Analysis" in tab_dict:
    with tab_dict["📅 Customer Month Analysis"]:
        st.subheader("Customer Month-wise Horizontal Breakdown")
        metric_choice = st.radio("Select Metric:", ["Sale Value (₹)", "Quantity (Qty)"], horizontal=True, key="month_choice_radio")
        val_col = 'SALEVAL' if "Sale Value" in metric_choice else 'QTY'
        df_cm = pd.concat([df_comp_kpi, df_base_kpi]).copy()
        
        if not df_cm.empty and 'CUSTOMERNAMEACTIVE' in df_cm.columns:
            month_order = df_cm.sort_values('BILLDATE')['MONTH_NAME'].unique().tolist()
            piv_m = df_cm.pivot_table(index='CUSTOMERNAMEACTIVE', columns=['MONTH_NAME', 'YEAR2'], values=val_col, aggfunc='sum', fill_value=0)
            cm_df = pd.DataFrame(index=piv_m.index)
            cm_df['CUSTOMERNAMEACTIVE'] = piv_m.index
            
            for m in month_order:
                ly_idx, ty_idx = (m, base_y), (m, comp_y)
                s_ly = piv_m[ly_idx] if ly_idx in piv_m.columns else pd.Series(0, index=piv_m.index)
                s_ty = piv_m[ty_idx] if ty_idx in piv_m.columns else pd.Series(0, index=piv_m.index)
                cm_df[f"{m} ({base_y})"] = s_ly
                cm_df[f"{m} ({comp_y})"] = s_ty
                cm_df[f"{m} Gr(%)"] = calc_growth_series(s_ly, s_ty)
                
            cm_df.index.name = None
            cm_df = cm_df.fillna(0).sort_values(by='CUSTOMERNAMEACTIVE', ascending=True)
            if not cm_df.empty:
                t_row_m = cm_df.sum(numeric_only=True).to_frame().T
                t_row_m['CUSTOMERNAMEACTIVE'] = "GRAND TOTAL"
                for m in month_order:
                    t_row_m[f"{m} Gr(%)"] = calc_growth(t_row_m[f"{m} ({base_y})"].iloc[0], t_row_m[f"{m} ({comp_y})"].iloc[0])
                cm_df = pd.concat([t_row_m, cm_df])
                
            if not compare_mode:
                cm_df = clean_df_for_single_mode(cm_df, base_y)
                
            for col in cm_df.columns:
                if col != 'CUSTOMERNAMEACTIVE':
                    if 'Gr(%)' in col: cm_df[col] = cm_df[col].map(lambda x: format_cell(x, col))
                    elif val_col == 'SALEVAL': cm_df[col] = cm_df[col].map(lambda x: format_indian_num(x, True))
                    else: cm_df[col] = cm_df[col].map(lambda x: format_indian_num(x, False))
            st.dataframe(style_dataframe(cm_df), use_container_width=True, hide_index=True)

if "🏷️ Discount & Contribution" in tab_dict:
    with tab_dict["🏷️ Discount & Contribution"]:
        st.subheader("🏷️ Discounting & Contribution Deep-Dive")

        if not selected_disc_col:
            st.warning("⚠️ Kripya global filters se 'Select Discount Column' dropdown mein sahi column select karein.")
        else:
            sel_disc_col = selected_disc_col

            df_disc = pd.concat([df_comp_kpi, df_base_kpi]).copy()

            tot_disc_comp = abs(df_disc[df_disc['YEAR2'] == comp_y][sel_disc_col].sum())
            tot_disc_base = abs(df_disc[df_disc['YEAR2'] == base_y][sel_disc_col].sum())
            
            tot_sale_comp = abs(df_disc[df_disc['YEAR2'] == comp_y]['SALEVAL'].sum())
            tot_sale_base = abs(df_disc[df_disc['YEAR2'] == base_y]['SALEVAL'].sum())

            gross_comp = tot_sale_comp + tot_disc_comp
            gross_base = tot_sale_base + tot_disc_base

            disc_pct_of_sales_comp = (tot_disc_comp / gross_comp * 100) if gross_comp > 0 else 0
            disc_pct_of_sales_base = (tot_disc_base / gross_base * 100) if gross_base > 0 else 0

            dk1, dk2, dk3 = st.columns(3)
            dk1.metric(f"Total Discount ({comp_y})", format_indian_num(tot_disc_comp, True), f"{calc_growth(tot_disc_base, tot_disc_comp):.1f}% (LY: {format_indian_num(tot_disc_base, True)})" if compare_mode else None, delta_color="inverse")
            if compare_mode:
                dk2.metric(f"Total Discount ({base_y})", format_indian_num(tot_disc_base, True))
            
            delta_disc_pct_str = f"{(disc_pct_of_sales_comp - disc_pct_of_sales_base):+.1f}% (LY: {disc_pct_of_sales_base:.1f}%)" if compare_mode else None
            dk3.metric(f"Discount % of Sales ({comp_y})", f"{disc_pct_of_sales_comp:.2f}%", delta=delta_disc_pct_str, delta_color="inverse")

            st.markdown("---")

            st.markdown("### 📅 1. Time-wise Discount Breakdown")
            disc_view = st.radio("Group Discount By:", ["Month-wise", "Day-wise", "Quarter-wise", "Year-wise"], horizontal=True, key="disc_time_view")

            start_month_num = ty_start_dt.month
            df_disc['F_Month'] = (df_disc['BILLDATE'].dt.month - start_month_num) % 12 + 1

            if disc_view == "Year-wise":
                p_disc_time = df_disc.pivot_table(index='YEAR2', values=sel_disc_col, aggfunc='sum').abs().reset_index()
                st.dataframe(p_disc_time, use_container_width=True, hide_index=True)
            else:
                if disc_view == "Day-wise":
                    df_disc['Sort'] = df_disc['F_Month'] * 100 + df_disc['BILLDATE'].dt.day
                    df_disc['Period'] = df_disc['BILLDATE'].dt.strftime('%d-%b')
                elif disc_view == "Month-wise":
                    df_disc['Sort'] = df_disc['F_Month']
                    df_disc['Period'] = df_disc['BILLDATE'].dt.strftime('%b')
                else: 
                    df_disc['Sort'] = (df_disc['F_Month'] - 1) // 3 + 1
                    df_disc['Period'] = "Q" + df_disc['Sort'].astype(str)

                p_disc = df_disc.pivot_table(index=['Sort', 'Period'], columns='YEAR2', values=sel_disc_col, aggfunc='sum', fill_value=0).abs()
                p_sale_d = df_disc.pivot_table(index=['Sort', 'Period'], columns='YEAR2', values='SALEVAL', aggfunc='sum', fill_value=0).abs()

                for y in [base_y, comp_y]:
                    if y not in p_disc.columns: p_disc[y] = 0
                    if y not in p_sale_d.columns: p_sale_d[y] = 0

                p_disc_df = pd.DataFrame({
                    'Period': p_disc.index.get_level_values('Period'),
                    f'Discount {base_y}': p_disc[base_y].values,
                    f'Discount {comp_y}': p_disc[comp_y].values,
                    'Discount Gr(%)': calc_growth_series(p_disc[base_y], p_disc[comp_y]).values
                })

                gross_base_arr = p_sale_d[base_y] + p_disc[base_y]
                gross_comp_arr = p_sale_d[comp_y] + p_disc[comp_y]

                p_disc_df[f'Disc % {base_y}'] = ((p_disc[base_y] / gross_base_arr * 100).replace([np.inf, -np.inf], 0).fillna(0)).values
                p_disc_df[f'Disc % {comp_y}'] = ((p_disc[comp_y] / gross_comp_arr * 100).replace([np.inf, -np.inf], 0).fillna(0)).values

                tot_d_ty = p_disc_df[f'Discount {comp_y}'].sum()
                p_disc_df['Discount Contribution (%)'] = (p_disc_df[f'Discount {comp_y}'] / tot_d_ty * 100).fillna(0) if tot_d_ty > 0 else 0

                c_seq_d = ['#A6C8E0', '#1F4E79'] if compare_mode else ['#1F4E79']
                fig_disc_time = px.bar(p_disc_df, x='Period', y=[f'Discount {base_y}', f'Discount {comp_y}'] if compare_mode else [f'Discount {comp_y}'], barmode='group', color_discrete_sequence=c_seq_d)
                st.plotly_chart(make_professional_chart(fig_disc_time, f"{disc_view} Discount Comparison" if compare_mode else f"{disc_view} Discount Summary"), use_container_width=True, key="disc_time_chart")

                p_disc_disp = p_disc_df.copy()
                if not compare_mode:
                    p_disc_disp = clean_df_for_single_mode(p_disc_disp, base_y)
                    
                for col in p_disc_disp.columns:
                    if col != 'Period':
                        if 'Gr(%)' in col: p_disc_disp[col] = p_disc_disp[col].map(lambda x: format_cell(x, 'Gr(%)'))
                        elif 'Contribution (%)' in col or 'Disc %' in col: p_disc_disp[col] = p_disc_disp[col].map(lambda x: f"{x:.1f}%")
                        else: p_disc_disp[col] = p_disc_disp[col].map(lambda x: format_indian_num(x, True))

                st.dataframe(style_dataframe(p_disc_disp), use_container_width=True, hide_index=True)

            st.markdown("---")

            st.markdown("### 👥 2. Party-wise Discount & Contribution Matrix")

            if 'CUSTOMERNAMEACTIVE' in df_disc.columns:
                p_cust_disc = df_disc.pivot_table(index='CUSTOMERNAMEACTIVE', columns='YEAR2', values=[sel_disc_col, 'SALEVAL'], aggfunc='sum', fill_value=0)

                d_ly = p_cust_disc[(sel_disc_col, base_y)].abs() if (sel_disc_col, base_y) in p_cust_disc.columns else pd.Series(0, index=p_cust_disc.index)
                d_ty = p_cust_disc[(sel_disc_col, comp_y)].abs() if (sel_disc_col, comp_y) in p_cust_disc.columns else pd.Series(0, index=p_cust_disc.index)
                s_ty = p_cust_disc[('SALEVAL', comp_y)].abs() if ('SALEVAL', comp_y) in p_cust_disc.columns else pd.Series(0, index=p_cust_disc.index)
                
                gross_ty_party = s_ty + d_ty

                party_disc_df = pd.DataFrame({
                    'Party Name': p_cust_disc.index,
                    f'Discount {base_y}': d_ly,
                    f'Discount {comp_y}': d_ty,
                    'Discount Gr(%)': calc_growth_series(d_ly, d_ty),
                    f'Sales {comp_y}': s_ty,
                    'Disc % of Sales': (d_ty / gross_ty_party * 100).fillna(0).replace([np.inf, -np.inf], 0)
                })

                tot_ty_party_disc = party_disc_df[f'Discount {comp_y}'].sum()
                party_disc_df['Discount Contribution (%)'] = (party_disc_df[f'Discount {comp_y}'] / tot_ty_party_disc * 100).fillna(0) if tot_ty_party_disc > 0 else 0

                party_disc_df = party_disc_df.sort_values(by=f'Discount {comp_y}', ascending=False)

                dc1, dc2 = st.columns(2)
                with dc1:
                    fig_top_party_disc = px.bar(party_disc_df.head(10), x='Party Name', y=f'Discount {comp_y}', color_discrete_sequence=['#E53935'])
                    st.plotly_chart(make_professional_chart(fig_top_party_disc, "Top 10 Highest Discount Parties"), use_container_width=True, key="top_party_disc_chart")
                with dc2:
                    fig_pie_disc = px.pie(party_disc_df.head(8), values=f'Discount {comp_y}', names='Party Name', color_discrete_sequence=px.colors.qualitative.Set3)
                    st.plotly_chart(make_professional_chart(fig_pie_disc, "Top Parties Discount Share %", is_pie=True), use_container_width=True, key="pie_disc_chart")

                t_row_p = party_disc_df.sum(numeric_only=True).to_frame().T
                t_row_p['Party Name'] = "GRAND TOTAL"
                t_row_p['Discount Gr(%)'] = calc_growth(t_row_p[f'Discount {base_y}'].iloc[0], t_row_p[f'Discount {comp_y}'].iloc[0])
                
                t_gross = t_row_p[f'Sales {comp_y}'].iloc[0] + t_row_p[f'Discount {comp_y}'].iloc[0]
                t_row_p['Disc % of Sales'] = (t_row_p[f'Discount {comp_y}'].iloc[0] / t_gross * 100) if t_gross > 0 else 0
                t_row_p['Discount Contribution (%)'] = 100.0

                party_disc_disp = pd.concat([t_row_p, party_disc_df]).reset_index(drop=True)

                if not compare_mode:
                    party_disc_disp = clean_df_for_single_mode(party_disc_disp, base_y)

                for col in party_disc_disp.columns:
                    if col != 'Party Name':
                        if 'Gr(%)' in col:
                            party_disc_disp[col] = party_disc_disp[col].map(lambda x: format_cell(x, col))
                        elif 'Contribution (%)' in col or 'Disc % of Sales' in col:
                            party_disc_disp[col] = party_disc_disp[col].map(lambda x: f"{x:.1f}%" if isinstance(x, (int, float)) else x)
                        else:
                            party_disc_disp[col] = party_disc_disp[col].map(lambda x: format_indian_num(x, True))

                st.dataframe(style_dataframe(party_disc_disp), use_container_width=True, hide_index=True)
            else:
                st.info("Customer Name column (`CUSTOMERNAMEACTIVE`) nahi mila.")

if "📊 Category vs Time" in tab_dict:
    with tab_dict["📊 Category vs Time"]: st.write("Category trends...")

if "🏆 Top Performers" in tab_dict:
    with tab_dict["🏆 Top Performers"]: st.write("Top Performers mapping...")

if "📔 Mega Ledger" in tab_dict:
    with tab_dict["📔 Mega Ledger"]:
        st.subheader("📔 Mega Ledger (Restricted by User Rights)")
        st.caption("Aapko sirf wahi headers dikhenge jinki aapko permission di gayi hai.")
        
        if pd.isna(allowed_columns_str) or allowed_columns_str == "ALL":
            display_df = filtered_df.copy()
        else:
            allowed_list = [c.strip() for c in allowed_columns_str.split(",")]
            valid_cols = [c for c in allowed_list if c in filtered_df.columns]
            display_df = filtered_df[valid_cols].copy()
            
        st.dataframe(display_df, use_container_width=True)

if "🚀 Advanced Analytics" in tab_dict:
    with tab_dict["🚀 Advanced Analytics"]:
        st.markdown("<h2 style='text-align: center; color: #1F4E79;'>🌟 PRO-MAX ADVANCED ANALYTICS SUITE 🌟</h2>", unsafe_allow_html=True)
        st.markdown("Yeh section completely isolated hai. Yahan lagaye gaye filters purane tabs ke data ko affect nahi karenge.")
        
        adv_col1, adv_col2, adv_col3 = st.columns(3)
        with adv_col1: top_n = st.slider("🏆 Select Top 'N' Categories for Funnel:", min_value=3, max_value=20, value=5)
        with adv_col2: day_type = st.radio("📅 Analyze Sale By Day Type:", ["All Days", "Weekday (Mon-Fri)", "Weekend (Sat-Sun)"], horizontal=True)
        with adv_col3:
            min_sale_val = float(df_comp_kpi['SALEVAL'].min()) if not df_comp_kpi.empty else 0.0
            max_sale_val = float(df_comp_kpi['SALEVAL'].max()) if not df_comp_kpi.empty else 100000.0
            if min_sale_val < max_sale_val: ticket_range = st.slider("💰 Ticket Size (Bill Value) Range Filter:", min_sale_val, max_sale_val, (min_sale_val, max_sale_val))
            else:
                ticket_range = (min_sale_val, max_sale_val)
                st.info(f"Only one ticket size available: {format_indian_num(min_sale_val, True)}")

        df_adv_comp = df_comp_kpi.copy()
        df_adv_base = df_base_kpi.copy()
        
        if day_type == "Weekday (Mon-Fri)":
            df_adv_comp = df_adv_comp[df_adv_comp['BILLDATE'].dt.dayofweek < 5]
            df_adv_base = df_adv_base[df_adv_base['BILLDATE'].dt.dayofweek < 5]
        elif day_type == "Weekend (Sat-Sun)":
            df_adv_comp = df_adv_comp[df_adv_comp['BILLDATE'].dt.dayofweek >= 5]
            df_adv_base = df_adv_base[df_adv_base['BILLDATE'].dt.dayofweek >= 5]
            
        df_adv_comp = df_adv_comp[(df_adv_comp['SALEVAL'] >= ticket_range[0]) & (df_adv_comp['SALEVAL'] <= ticket_range[1])]
        st.markdown("---")
        
        if compare_mode:
            st.markdown(f"### 🌉 YoY Sales Bridge (LY vs TY)")
            st.caption("Yeh chart dikhata hai ki Last Year ki sale se chal kar, growing stores ne kitna add kiya aur declining stores ne kitna kam kiya taaki This Year ki sale bani.")
            
            ly_total_bridge = df_adv_base['SALEVAL'].sum()
            ty_total_bridge = df_adv_comp['SALEVAL'].sum()
            
            if 'CUSTOMERNAMEACTIVE' in df_adv_comp.columns:
                cust_base_bridge = df_adv_base.groupby('CUSTOMERNAMEACTIVE')['SALEVAL'].sum()
                cust_comp_bridge = df_adv_comp.groupby('CUSTOMERNAMEACTIVE')['SALEVAL'].sum()
                cust_all_bridge = pd.DataFrame({'LY': cust_base_bridge, 'TY': cust_comp_bridge}).fillna(0)
                cust_all_bridge['Delta'] = cust_all_bridge['TY'] - cust_all_bridge['LY']
                
                growth_val = cust_all_bridge[cust_all_bridge['Delta'] > 0]['Delta'].sum()
                decline_val = cust_all_bridge[cust_all_bridge['Delta'] < 0]['Delta'].sum()
                
                fig_waterfall = go.Figure(go.Waterfall(
                    name = "Sales Bridge", orientation = "v",
                    measure = ["absolute", "relative", "relative", "total"],
                    x = [f"LY Sale ({base_y})", "Growing Stores (+)", "Declining Stores (-)", f"TY Sale ({comp_y})"],
                    textposition = "outside",
                    text = [format_indian_num(ly_total_bridge), f"+{format_indian_num(growth_val)}", f"{format_indian_num(decline_val)}", format_indian_num(ty_total_bridge)],
                    y = [ly_total_bridge, growth_val, decline_val, ty_total_bridge],
                    connector = {"line":{"color":"rgb(63, 63, 63)"}},
                    decreasing = {"marker":{"color":"#E53935"}},
                    increasing = {"marker":{"color":"#4CAF50"}},
                    totals = {"marker":{"color":"#1F4E79"}}
                ))
                fig_waterfall.update_layout(title={'text': "Revenue Bridge: How we reached TY Sales", 'font': {'size': 20, 'weight': 'bold'}, 'x': 0.02}, waterfallgap=0.3, template='plotly_white')
                st.plotly_chart(fig_waterfall, use_container_width=True)
            else:
                st.warning("Waterfall chart ke liye 'CUSTOMERNAMEACTIVE' column ki zarurat hai.")
        else:
            st.info("⚠️ Waterfall Chart dekhne ke liye global filters se 'Enable Comparison (LY)' ON karein.")
            
        st.markdown("---")
        if 'CATEGORY' in df_adv_comp.columns:
            st.markdown(f"### 🌪️ Category Contribution Funnel (Top {top_n})")
            funnel_df = df_adv_comp.groupby('CATEGORY')['SALEVAL'].sum().reset_index().sort_values('SALEVAL', ascending=False).head(top_n)
            if not funnel_df.empty:
                funnel_df['TEXT_VAL'] = funnel_df['SALEVAL'].apply(lambda x: format_indian_num(x, True))
                fig_funnel = px.funnel(funnel_df, x='SALEVAL', y='CATEGORY', text='TEXT_VAL', color_discrete_sequence=['#1F4E79'])
                fig_funnel.update_layout(title={'text': f"Top {top_n} Categories Flow", 'font': {'size': 20, 'weight': 'bold'}, 'x': 0.02}, template='plotly_white')
                st.plotly_chart(fig_funnel, use_container_width=True)

        st.markdown("<br><br><hr style='border: 2px dashed #1F4E79;'>", unsafe_allow_html=True)
        pm_tab_map, pm_tab_rfm, pm_tab_gauge, pm_tab_basket, pm_tab_price, pm_tab_ai, pm_tab_report = st.tabs([
            "🗺️ Geo Map", "🎯 RFM Segmentation", "⏱️ Speedometer", 
            "🛒 Basket Analysis", "📉 Price Sensitivity", "🔮 AI Forecast", "📩 Auto Report"
        ])

        with pm_tab_map:
            st.subheader("🗺️ Geographical Sales Heatmap")
            if 'STATE' in df_comp_kpi.columns:
                state_coords = {
                    'MAHARASHTRA': (19.7515, 75.7139), 'DELHI': (28.7041, 77.1025), 'KARNATAKA': (15.3173, 75.7139),
                    'GUJARAT': (22.2587, 71.1924), 'TELANGANA': (18.1124, 79.0193), 'TAMIL NADU': (11.1271, 78.6569),
                    'WEST BENGAL': (22.9868, 87.8550), 'RAJASTHAN': (27.0238, 74.2179), 'UTTAR PRADESH': (26.8467, 80.9462),
                    'MADHYA PRADESH': (22.9734, 78.6569), 'PUNJAB': (31.1471, 75.3412), 'HARYANA': (29.0588, 76.0856),
                    'KERALA': (10.8505, 76.2711), 'BIHAR': (25.0961, 85.3131), 'ODISHA': (20.9517, 85.0985),
                    'ASSAM': (26.2006, 92.9376), 'JHARKHAND': (23.6102, 85.2799), 'CHHATTISGARH': (21.2787, 81.8661),
                    'UTTARAKHAND': (30.0668, 79.0193), 'HIMACHAL PRADESH': (31.1048, 77.1734), 'JAMMU AND KASHMIR': (33.7782, 76.5762),
                    'GOA': (15.2993, 74.1240), 'CHANDIGARH': (30.7333, 76.7794), 'ANDHRA PRADESH': (15.9129, 79.7400)
                }
                map_df = df_comp_kpi.groupby('STATE').agg({'SALEVAL': 'sum', 'QTY': 'sum'}).reset_index()
                map_df['LAT'] = map_df['STATE'].apply(lambda x: state_coords.get(str(x).upper().strip(), (None, None))[0])
                map_df['LON'] = map_df['STATE'].apply(lambda x: state_coords.get(str(x).upper().strip(), (None, None))[1])
                map_df = map_df.dropna(subset=['LAT', 'LON'])
                if not map_df.empty:
                    map_df['Hover Text'] = map_df.apply(lambda row: f"State: {row['STATE']}<br>Sale: {format_indian_num(row['SALEVAL'], True)}<br>Qty: {format_indian_num(row['QTY'], False)}", axis=1)
                    fig_map = px.scatter_mapbox(
                        map_df, lat="LAT", lon="LON", size="SALEVAL", color="SALEVAL", 
                        hover_name="STATE", hover_data={"LAT": False, "LON": False, "SALEVAL": False}, 
                        text="Hover Text", color_continuous_scale=px.colors.sequential.Teal, 
                        size_max=40, zoom=3.5, center={"lat": 22.0, "lon": 79.0}, mapbox_style="open-street-map"
                    )
                    fig_map.update_traces(hovertemplate="%{text}")
                    min_sale_val_m, max_sale_val_m = map_df['SALEVAL'].min(), map_df['SALEVAL'].max()
                    tick_v = np.linspace(min_sale_val_m, max_sale_val_m, num=5)
                    tick_t = [format_indian_num(v, is_currency=True) for v in tick_v]
                    fig_map.update_layout(
                        margin={"r":0,"t":40,"l":0,"b":0}, 
                        title={'text': 'Sales Distribution Across India', 'font': {'size': 20, 'weight': 'bold'}},
                        coloraxis_colorbar=dict(title="Total Sales", tickmode="array", tickvals=tick_v, ticktext=tick_t)
                    )
                    st.plotly_chart(fig_map, use_container_width=True)
                else: st.info("Map render karne ke liye 'STATE' column ka valid Indian states ke naam hona zaruri hai.")
            else: st.warning("Map ke liye 'STATE' column data mein missing hai.")

        with pm_tab_rfm:
            st.subheader("🎯 RFM (Recency, Frequency, Monetary) Segmentation")
            st.caption("AI-Driven categorisation of stores based on their buying behaviour.")
            if 'CUSTOMERNAMEACTIVE' in df_comp_kpi.columns and 'UNIQUE_BILL_ID' in df_comp_kpi.columns:
                last_date = df_comp_kpi['BILLDATE'].max()
                rfm = df_comp_kpi.groupby('CUSTOMERNAMEACTIVE').agg(
                    Recency=('BILLDATE', lambda x: (last_date - x.max()).days),
                    Frequency=('UNIQUE_BILL_ID', 'nunique'),
                    Monetary=('SALEVAL', 'sum')
                ).reset_index()
                try:
                    rfm['R'] = pd.qcut(rfm['Recency'].rank(method='first'), q=4, labels=range(4, 0, -1))
                    rfm['F'] = pd.qcut(rfm['Frequency'].rank(method='first'), q=4, labels=range(1, 5))
                    rfm['M'] = pd.qcut(rfm['Monetary'].rank(method='first'), q=4, labels=range(1, 5))
                    rfm['RFM_Segment'] = rfm.apply(lambda x: str(x['R']) + str(x['F']) + str(x['M']), axis=1)
                    def rfm_level(df):
                        score = int(df['RFM_Segment'])
                        if score >= 444: return '🌟 Champions'
                        elif score >= 333: return '🤝 Loyal Customers'
                        elif score >= 222: return '⚠️ Needs Attention'
                        else: return '🚨 At Risk'
                    rfm['Customer Grade'] = rfm.apply(rfm_level, axis=1)
                    fig_rfm = px.treemap(rfm, path=['Customer Grade', 'CUSTOMERNAMEACTIVE'], values='Monetary', color='Monetary', color_continuous_scale='Blues')
                    st.plotly_chart(make_professional_chart(fig_rfm, "RFM Customer Portfolio Heatmap"), use_container_width=True)
                except ValueError: st.info("RFM model chalane ke liye aur data points (customers) ki zarurat hai.")
            else: st.warning("Customer Name ya Unique Bill ID missing hai.")

        with pm_tab_gauge:
            st.subheader("⏱️ Speedometer: Target vs Achievement")
            st.caption("Adjust target below to see dynamic achievement gauge.")
            col_t1, col_t2 = st.columns([1, 2])
            current_sale = float(df_comp_kpi['SALEVAL'].sum())
            with col_t1:
                st.markdown("<br>", unsafe_allow_html=True)
                default_target = current_sale * 1.2 if current_sale > 0 else 1000000
                target_val = st.number_input("Set Your Sales Target (₹)", min_value=1, value=int(default_target), step=10000)
            with col_t2:
                fig_gauge = go.Figure(go.Indicator(
                    mode = "gauge+number+delta", value = current_sale, domain = {'x': [0, 1], 'y': [0, 1]},
                    title = {'text': "Sales Target Achievement", 'font': {'size': 20}},
                    delta = {'reference': target_val, 'increasing': {'color': "green"}, 'decreasing': {'color': "red"}},
                    gauge = {
                        'axis': {'range': [None, target_val * 1.5], 'tickwidth': 1, 'tickcolor': "darkblue"},
                        'bar': {'color': "#1F4E79"}, 'bgcolor': "white", 'borderwidth': 2, 'bordercolor': "gray",
                        'steps': [{'range': [0, target_val * 0.5], 'color': '#ffcdd2'}, {'range': [target_val * 0.5, target_val * 0.9], 'color': '#fff9c4'}, {'range': [target_val * 0.9, target_val * 1.5], 'color': '#c8e6c9'}],
                        'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': target_val}
                    }
                ))
                st.plotly_chart(fig_gauge, use_container_width=True)

        with pm_tab_basket:
            st.subheader("🛒 Market Basket (Categories bought together)")
            if 'CATEGORY' in df_comp_kpi.columns and 'UNIQUE_BILL_ID' in df_comp_kpi.columns:
                basket = df_comp_kpi.groupby(['UNIQUE_BILL_ID', 'CATEGORY'])['QTY'].sum().unstack().reset_index().fillna(0).set_index('UNIQUE_BILL_ID')
                basket_sets = (basket > 0).astype(int)
                if len(basket_sets.columns) > 1:
                    co_matrix = basket_sets.T.dot(basket_sets)
                    for i in range(len(co_matrix.columns)): co_matrix.iloc[i, i] = 0
                    fig_matrix = px.imshow(co_matrix, text_auto=True, color_continuous_scale='Purples', aspect="auto", labels=dict(x="Category 1", y="Category 2", color="Co-occurrences"))
                    fig_matrix.update_layout(title="Cross-Selling Heatmap (Count of shared bills)")
                    st.plotly_chart(fig_matrix, use_container_width=True)
                else: st.info("Basket analysis ke liye ek se zyada category ka data hona zaruri hai.")
            else: st.warning("UNIQUE_BILL_ID ya CATEGORY column nahi mila.")

        with pm_tab_price:
            st.subheader("📉 Price Sensitivity (Impact of Discount on Volume)")
            if selected_disc_col and 'CATEGORY' in df_comp_kpi.columns:
                sens_df = df_comp_kpi.groupby('CATEGORY').agg(SALE=('SALEVAL', 'sum'), QTY=('QTY', 'sum'), DISC=(selected_disc_col, 'sum')).reset_index()
                sens_df['DISC'] = sens_df['DISC'].abs()
                sens_df['Gross'] = sens_df['SALE'].abs() + sens_df['DISC']
                sens_df['Disc %'] = (sens_df['DISC'] / sens_df['Gross'] * 100).fillna(0)
                sens_df = sens_df[sens_df['QTY'] > 0]
                fig_scatter = px.scatter(sens_df, x='Disc %', y='QTY', size='SALE', color='CATEGORY', hover_name='CATEGORY', size_max=40, template='plotly_white')
                fig_scatter.update_layout(title="Category-wise Volume elasticity against Discounts", xaxis_title="Average Discount %", yaxis_title="Total Qty Sold")
                st.plotly_chart(fig_scatter, use_container_width=True)
            else: st.info("Global filters mein Discount column select karein.")

        with pm_tab_ai:
            st.subheader("🔮 Predictive Sales Forecast (Next 15 Days)")
            st.caption("Historical daily data ke base par AI-driven trend line.")
            daily_sales = df_comp_kpi.groupby(df_comp_kpi['BILLDATE'].dt.date)['SALEVAL'].sum().reset_index()
            daily_sales.columns = ['Date', 'Actual_Sales']
            if len(daily_sales) > 5:
                daily_sales['Date'] = pd.to_datetime(daily_sales['Date'])
                last_date_ai = daily_sales['Date'].max()
                future_dates = [last_date_ai + timedelta(days=i) for i in range(1, 16)]
                ewma_trend = daily_sales['Actual_Sales'].ewm(span=7, adjust=False).mean().iloc[-1]
                future_df = pd.DataFrame({'Date': future_dates, 'Forecast_Sales': [ewma_trend] * 15})
                fig_ai = go.Figure()
                fig_ai.add_trace(go.Scatter(x=daily_sales['Date'], y=daily_sales['Actual_Sales'], mode='lines+markers', name='Actual Sales', line=dict(color='#1F4E79', width=2)))
                fig_ai.add_trace(go.Scatter(x=future_df['Date'], y=future_df['Forecast_Sales'], mode='lines', name='AI Predicted Trend', line=dict(color='#E53935', width=2, dash='dash')))
                fig_ai.update_layout(title="Sales Trend & Near-Future Projection", xaxis_title="Date", yaxis_title="Sale Value", template='plotly_white')
                st.plotly_chart(fig_ai, use_container_width=True)
            else: st.info("Forecasting algorithm ke liye kam se kam 5 din ka continuous data chahiye.")

        with pm_tab_report:
            st.subheader("📩 Management Auto-Report System")
            st.markdown("Is button par click karke aap direct Management ko dashboard ka summarized snap (Total Sale, Qty, Top Store) bhej sakte hain (Simulated).")
            report_email = st.text_input("Enter Boss/Manager Email ID:", "manager@company.com")
            if st.button("🚀 Trigger Management Email Report", type="primary"):
                with st.spinner("Compiling insights and generating report..."):
                    import time
                    time.sleep(1.5)
                    top_store_name = "N/A"
                    if 'CUSTOMERNAMEACTIVE' in df_comp_kpi.columns and not df_comp_kpi.empty:
                        top_store_name = df_comp_kpi.groupby('CUSTOMERNAMEACTIVE')['SALEVAL'].sum().idxmax()
                    st.success(f"✅ Successfully sent to **{report_email}**!")
                    st.info(f"**Preview of Sent Email:**\n- 📈 **Total TY Sale:** {format_indian_num(df_comp_kpi['SALEVAL'].sum(), True)}\n- 📦 **Total TY Qty:** {format_indian_num(df_comp_kpi['QTY'].sum(), False)}\n- 🏆 **Top Store:** {top_store_name}\n- 📅 **Period:** {ty_start.strftime('%d %b %Y')} to {ty_end.strftime('%d %b %Y')}")

# =====================================================================
# ⚙️ VIP SUPER ADMIN CONTROL PANEL (ONLY FOR GOD)
# =====================================================================
if "⚙️ Admin Control Panel" in tab_dict:
    with tab_dict["⚙️ Admin Control Panel"]:
        st.markdown("<h2 style='color:#D32F2F;'>⚙️ Super Admin Operations Center</h2>", unsafe_allow_html=True)
        st.success("✅ Welcome GOD! This is your secured area to manage the entire platform.")
        
        users_df_current = get_users_db()
        
        st.markdown("### 1️⃣ User Base & Core Rights Management")
        st.caption("Manage Usernames, Passwords, and Data Access File Roles (AR/FM/ALL).")
        edited_df = st.data_editor(
            users_df_current[['Username', 'Password', 'Role']], 
            num_rows="dynamic",
            column_config={
                "Username": st.column_config.TextColumn("👤 Username", required=True),
                "Password": st.column_config.TextColumn("🔑 Password", required=True),
                "Role": st.column_config.SelectboxColumn("🛡️ Target Data Role", options=["ADMIN", "ALL", "AR", "FM"], required=True)
            },
            use_container_width=True
        )
        
        st.markdown("---")
        st.markdown("### 2️⃣ Application Access Rules (Columns, Tabs, Features)")
        st.caption("Select a specific user below to define what components they can see across the application.")
        
        user_to_edit = st.selectbox("📌 Select Target User to Manage Rules:", users_df_current['Username'])
        current_cols_raw = users_df_current.loc[users_df_current['Username'] == user_to_edit, 'Allowed_Columns'].values[0]
        current_tabs_raw = users_df_current.loc[users_df_current['Username'] == user_to_edit, 'Allowed_Tabs'].values[0]
        current_feat_raw = users_df_current.loc[users_df_current['Username'] == user_to_edit, 'Allowed_Features'].values[0]
        
        all_cols_list = list(sheet_data.columns)
        all_features_list = ["File Upload Feature", "File Selector", "Data View Selector", "Compare LY Toggle", "Quick Range Preset", "Reload Data Button", "PDF Export Button"]
        
        def_cols = all_cols_list if pd.isna(current_cols_raw) or current_cols_raw == "ALL" else [c.strip() for c in current_cols_raw.split(",") if c.strip() in all_cols_list]
        def_tabs = MASTER_TABS if pd.isna(current_tabs_raw) or current_tabs_raw == "ALL" else [t.strip() for t in current_tabs_raw.split(",") if t.strip() in MASTER_TABS]
        def_feat = all_features_list if pd.isna(current_feat_raw) or current_feat_raw == "ALL" else [f.strip() for f in current_feat_raw.split(",") if f.strip() in all_features_list]

        a_col1, a_col2, a_col3 = st.columns(3)
        with a_col1: selected_col_rights = st.multiselect("👁️ Permitted Mega-Ledger Columns:", all_cols_list, default=def_cols)
        with a_col2: selected_tab_rights = st.multiselect("📂 Permitted Dashboard Tabs:", MASTER_TABS, default=def_tabs)
        with a_col3: selected_feat_rights = st.multiselect("⚙️ Permitted Global Features:", all_features_list, default=def_feat)
        
        if st.button("💾 Enforce Security Settings", type="primary", use_container_width=True):
            final_db = edited_df.copy()
            final_db = final_db.merge(users_df_current[['Username', 'Allowed_Columns', 'Allowed_Tabs', 'Allowed_Features']], on='Username', how='left')
            
            final_db.loc[final_db['Username'] == user_to_edit, 'Allowed_Columns'] = "ALL" if len(selected_col_rights) == len(all_cols_list) or not selected_col_rights else ",".join(selected_col_rights)
            final_db.loc[final_db['Username'] == user_to_edit, 'Allowed_Tabs'] = "ALL" if len(selected_tab_rights) == len(MASTER_TABS) or not selected_tab_rights else ",".join(selected_tab_rights)
            final_db.loc[final_db['Username'] == user_to_edit, 'Allowed_Features'] = "ALL" if len(selected_feat_rights) == len(all_features_list) or not selected_feat_rights else ",".join(selected_feat_rights)
            
            final_db.to_csv("users_db.csv", index=False)
            st.success("🎉 Global Security & Access Rules Updated Successfully! (Refresh Dashboard to apply changes)")
            st.balloons()