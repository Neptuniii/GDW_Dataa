import streamlit as st
import pandas as pd
import os
from st_aggrid import AgGrid, GridOptionsBuilder
from streamlit_js_eval import streamlit_js_eval

st.set_page_config(layout="wide")

resolution = streamlit_js_eval(js_expressions='screen.width', key='SCR')
if resolution is None:
    st.stop()
is_mobile = resolution < 768

st.sidebar.header("📂 Chọn dữ liệu muốn xem")

data_folder = "data"
csv_files = [f for f in os.listdir(data_folder) if f.endswith(".csv")]

if not csv_files:
    st.error("Không tìm thấy file CSV trong thư mục `data/`.")
    st.stop()

display_names = {
    "naphaluancod_2025-07-16.csv": "🔹 Trước SOS5",
    "naphaluancod_2025-07-22.csv": "🔸 Sau SOS5"
}

csv_files = [f for f in csv_files if f in display_names]

selected_file = st.sidebar.selectbox(
    "Chọn dữ liệu :",
    options=csv_files,
    format_func=lambda x: display_names.get(x, x)
)

df = pd.read_csv(os.path.join(data_folder, selected_file), usecols=[
    'governor_id', 'governor_name', 'historical_highest_power',
    'units_killed', 'units_dead', 'units_healed',
    'gold_spent', 'wood_spent', 'stone_spent', 'mana_spent', 'gems_spent',
    'tier_1_kills', 'tier_2_kills', 'tier_3_kills', 'tier_4_kills', 'tier_5_kills',
])

df = df.rename(columns={
    'governor_id': 'ID',
    'governor_name': 'Name',
    'historical_highest_power': 'Highest Power',
    'units_killed': 'Total kill',
    'units_dead': 'Total dead',
    'units_healed': 'Total healed',
    'tier_1_kills': 'T1 kill',
    'tier_2_kills': 'T2 kill',
    'tier_3_kills': 'T3 kill',
    'tier_4_kills': 'T4 kill',
    'tier_5_kills': 'T5 kill',
    'gold_spent': 'Gold spent',
    'wood_spent': 'Wood spent',
    'stone_spent': 'Stone spent',
    'mana_spent': 'Mana spent',
    'gems_spent': 'Gem spent'
})

for tier in ['T1', 'T2', 'T3', 'T4', 'T5']:
    kill_col = f"{tier} kill"
    pct_col = f"{tier}/Total (%)"
    df[pct_col] = (df[kill_col] / df['Total kill'].replace(0, pd.NA)) * 100
    df[pct_col] = df[pct_col].round(2)

st.title(f"GDW Data – {display_names[selected_file]}")
st.title("By Neptuniii")

search = st.text_input("🔍 Tìm theo ID hoặc Tên:")
if search:
    search_lower = search.lower()
    filtered_df = df[
        df['ID'].astype(str).str.contains(search_lower) |
        df['Name'].str.lower().str.contains(search_lower)
    ]
else:
    filtered_df = df

filtered_df = filtered_df.reset_index(drop=True)
filtered_df.index = filtered_df.index + 1

general_cols = ['ID', 'Name', 'Highest Power', 'Total kill', 'Total dead', 'Total healed']
resource_cols = ['Gold spent', 'Wood spent', 'Stone spent', 'Mana spent', 'Gem spent']
kill_cols_ordered = []
for tier in ['T1', 'T2', 'T3', 'T4', 'T5']:
    kill_cols_ordered.append(f"{tier} kill")
    kill_cols_ordered.append(f"{tier}/Total (%)")

df_general = filtered_df[general_cols]
df_resources = filtered_df[['ID', 'Name'] + resource_cols]
df_kills = filtered_df[['ID', 'Name', 'Total kill'] + kill_cols_ordered]

def show_aggrid(df_to_show, height=400):
    gb = GridOptionsBuilder.from_dataframe(df_to_show)
    for col in df_to_show.columns:
        if col == "ID":
            gb.configure_column("ID", width=90, cellStyle={'textAlign': 'left'})
            continue
        if col == "Name":
            gb.configure_column("Name", width=160)
            continue
        if df_to_show[col].dtype.kind in 'iuf':
            if "/Total (%)" in col:
                gb.configure_column(
                    col, type=["numericColumn", "numberColumnFilter", "customNumericFormat"],
                    precision=2, valueFormatter="x.toFixed(2) + '%'")
            else:
                gb.configure_column(
                    col, type=["numericColumn", "numberColumnFilter", "customNumericFormat"],
                    precision=0 if df_to_show[col].dtype.kind in 'iu' else 2,
                    valueFormatter="x.toLocaleString()")
    gb.configure_default_column(resizable=True, minWidth=100)
    gridOptions = gb.build()

    AgGrid(df_to_show,
           gridOptions=gridOptions,
           height=height,
           fit_columns_on_grid_load=not is_mobile,
           allow_unsafe_jscode=True)

st.subheader("🧮 Thông tin cơ bản")
show_aggrid(df_general)

st.subheader("🪙 Tài nguyên đã tiêu")
show_aggrid(df_resources)

st.subheader("⚔️ Số lượng kill theo từng tier")
show_aggrid(df_kills, height=500)
