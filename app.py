import streamlit as st
import pandas as pd

# --- Page Configuration & Pitch-Black Theme Styling ---
st.set_page_config(
    page_title="Pokémon Master Set Dex",
    page_icon="⚡",
    layout="wide"
)

st.markdown("""
    <style>
    .stApp {
        background-color: #121212;
        color: #E0E0E0;
    }
    .card-box {
        background-color: #1E1E1E;
        border: 1px solid #2C2C2C;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .have-badge {
        background-color: #003311;
        color: #00FF66;
        padding: 4px 10px;
        border-radius: 5px;
        font-weight: bold;
        font-size: 0.85em;
    }
    .missing-badge {
        background-color: #330000;
        color: #FF5C5C;
        padding: 4px 10px;
        border-radius: 5px;
        font-weight: bold;
        font-size: 0.85em;
    }
    .metric-card {
        background-color: #1A1A1A;
        border: 1px solid #333333;
        padding: 20px;
        border-radius: 8px;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# --- Google Sheets Public Connection ---
# Replace this with your actual Google Sheet ID from your URL (the long string between /d/ and /edit)
SPREADSHEET_ID = "/d/1dIzgb3cwAahXU1B-NGsqt5wgzU-sm38-Ts-SnFfWYDQ/edit?pli=1&gid=1102552568#gid=1102552568" 

# Define your tab names and their corresponding GIDs (found at the end of your browser URL when clicking a tab)
SHEETS_MAP = {
    "Pitch Black": "0", # Usually the first tab is gid=0
    "Chaos Rising": "12345678", # Replace with your actual tab gid numbers
    "Delta Reign": "87654321",
    "Perfect Order": "11223344"
}

st.title("⚡ Pokémon Master Set Pokédex")
st.markdown("Visual Collection Tracker • Pitch Black Theme Edition")

# Set Selector Sidebar
selected_sheet_name = st.sidebar.selectbox("Select Set / Tab", list(SHEETS_MAP.keys()))

@st.cache_data(ttl=600)
def load_sheet_data(sheet_id, gid):
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
    return pd.read_csv(url)

try:
    gid = SHEETS_MAP[selected_sheet_name]
    df = load_sheet_data(SPREADSHEET_ID, gid)
except Exception as e:
    st.error(f"Failed to load Google Sheet. Check your Sheet ID and GIDs. Error: {e}")
    st.stop()

# Ensure expected columns exist
expected_headers = ['Card #', 'Card Name', 'Regular Qty', 'Reverse Holo Qty', 'Holo / Ultra Rare Qty', 'Status']
for col in expected_headers:
    if col not in df.columns and col != 'Status':
        df[col] = 0

# Ensure numeric quantities
for col in ['Regular Qty', 'Reverse Holo Qty', 'Holo / Ultra Rare Qty']:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

# Calculate dynamic status if empty
if 'Status' not in df.columns or df['Status'].isna().all():
    df['Status'] = df.apply(lambda r: 'HAVE' if (r['Regular Qty'] + r['Reverse Holo Qty'] + r['Holo / Ultra Rare Qty']) > 0 else 'MISSING', axis=1)

# --- Top KPI Summary Dashboard ---
total_cards = len(df)
owned_cards = len(df[df['Status'] == 'HAVE'])
needed_cards = total_cards - owned_cards
completion_rate = (owned_cards / total_cards) * 100 if total_cards > 0 else 0

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"""
        <div class="metric-card">
            <h3>Cards Owned</h3>
            <h1 style="color: #00FF66;">{owned_cards}</h1>
        </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown(f"""
        <div class="metric-card">
            <h3>Cards Needed</h3>
            <h1 style="color: #FF5C5C;">{needed_cards}</h1>
        </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown(f"""
        <div class="metric-card">
            <h3>Completion Rate</h3>
            <h1 style="color: #3399FF;">{completion_rate:.1f}%</h1>
        </div>
    """, unsafe_allow_html=True)

st.divider()

# --- View Toggle & Filters ---
view_mode = st.sidebar.radio("View Mode", ["Pokédex Grid", "Detailed Table"])
status_filter = st.sidebar.selectbox("Filter Status", ["All", "HAVE", "MISSING"])

filtered_df = df.copy()
if status_filter != "All":
    filtered_df = filtered_df[filtered_df['Status'] == status_filter]

# --- Pokédex Grid View ---
if view_mode == "Pokédex Grid":
    st.subheader(f"📖 {selected_sheet_name} Pokédex Grid")
    
    cols_per_row = 4
    grid_cols = st.columns(cols_per_row)
    
    for index, row in filtered_df.reset_index().iterrows():
        col_idx = index % cols_per_row
        with grid_cols[col_idx]:
            status_class = "have-badge" if str(row['Status']).strip() == 'HAVE' else "missing-badge"
            reg = row.get('Regular Qty', 0)
            rev = row.get('Reverse Holo Qty', 0)
            holo = row.get('Holo / Ultra Rare Qty', 0)
            
            st.markdown(f"""
                <div class="card-box">
                    <span style="color: #888; font-size: 0.9em;">{row.get('Card #', '')}</span>
                    <h4 style="margin: 5px 0; color: #FFF;">{row.get('Card Name', '')}</h4>
                    <span class="{status_class}">{row.get('Status', 'MISSING')}</span>
                    <p style="margin-top: 10px; font-size: 0.85em; color: #BBB;">
                        Reg: {reg} | Rev: {rev} | Holo/ex: {holo}
                    </p>
                </div>
            """, unsafe_allow_html=True)

# --- Detailed Table View ---
else:
    st.subheader(f"📋 {selected_sheet_name} Collection Table")
    st.dataframe(
        filtered_df[[c for c in expected_headers if c in filtered_df.columns]],
        use_container_width=True,
        hide_index=True
    )
