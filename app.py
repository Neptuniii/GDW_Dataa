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

data_folder = "data"
file_before = "naphaluancod_2025-07-16.csv"
file_after = "naphaluancod_2025-07-22.csv"

st.subheader("📂 Chọn dữ liệu muốn xem")
col1, col2 = st.columns([1, 4])  # col1 nhỏ hơn
with col1:
    selected_mode = st.selectbox(
        "Chọn dữ liệu:",
        options=["before", "after", "diff"],
        format_func=lambda x: {
            "before": "🔹 Trước SOS5",
            "after": "🔸 Sau SOS5",
            "diff": "⚔️  SOS5"
        }[x]
    )


def preprocess(df):
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
        'gems_spent': 'Gem spent',
        'gold_gathered': 'Gold gathered',
        'wood_gathered': 'Wood gathered',
        'ore_gathered': 'Ore gathered',
        'mana_gathered': 'Mana gathered'
    })
    return df

df_before = preprocess(pd.read_csv(os.path.join(data_folder, file_before)))
df_after = preprocess(pd.read_csv(os.path.join(data_folder, file_after)))

if selected_mode == "before":
    df = df_before.copy()
    selected_file = file_before
elif selected_mode == "after":
    df = df_after.copy()
    selected_file = file_after
else:
    selected_file = "diff"
    df_merged = pd.merge(df_after, df_before, on="ID", suffixes=("_after", "_before"))
    result = pd.DataFrame()
    result["ID"] = df_merged["ID"]
    result["Name"] = df_merged["Name_before"]  # Giữ tên từ file trước

    for col in df_after.columns:
        if col in ["ID", "Name"]:
            continue
        if col in df_before.columns:
            col_after = f"{col}_after"
            col_before = f"{col}_before"
            result[col] = pd.to_numeric(df_merged[col_after], errors="coerce") - \
                          pd.to_numeric(df_merged[col_before], errors="coerce")

    df = result

for tier in ['T1', 'T2', 'T3', 'T4', 'T5']:
    kill_col = f"{tier} kill"
    if kill_col in df.columns and "Total kill" in df.columns:
        pct_col = f"{tier}/Total (%)"
        df[kill_col] = pd.to_numeric(df[kill_col], errors='coerce')
        df["Total kill"] = pd.to_numeric(df["Total kill"], errors='coerce')

        df[pct_col] = df.apply(
            lambda row: round((row[kill_col] / row["Total kill"] * 100), 2)
            if pd.notna(row[kill_col]) and pd.notna(row["Total kill"]) and row["Total kill"] != 0
            else None,
            axis=1
        )

title_map = {
    file_before: "🔹 Trước SOS5",
    file_after: "🔸 Sau SOS5",
    "diff": "⚔️ Trong SOS5 (Chênh lệch)"
}
st.title(f"GDW Data – {title_map[selected_file]}")
# Xóa khi có dữ liệu thật
if selected_file == file_after or selected_mode == "diff":
    st.markdown("*Đây là dữ liệu test, không có thật. \nTest với id = 11970924*")

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
filtered_df.index += 1

general_cols = ['ID', 'Name', 'Highest Power', 'Total kill', 'Total dead', 'Total healed']
resource_cols = ['Gold spent', 'Wood spent', 'Stone spent', 'Mana spent', 'Gem spent']
kill_cols_ordered = []
for tier in ['T1', 'T2', 'T3', 'T4', 'T5']:
    kill_cols_ordered.append(f"{tier} kill")
    kill_cols_ordered.append(f"{tier}/Total (%)")

df_general = filtered_df[[col for col in general_cols if col in filtered_df.columns]]
df_resources = filtered_df[['ID', 'Name'] + [col for col in resource_cols if col in filtered_df.columns]]
df_kills = filtered_df[['ID', 'Name', 'Total kill'] + [col for col in kill_cols_ordered if col in filtered_df.columns]]

if selected_mode == "diff":
    gather_cols = ['Gold gathered', 'Wood gathered', 'Ore gathered', 'Mana gathered']
    df_gather = filtered_df[['ID', 'Name'] + [col for col in gather_cols if col in filtered_df.columns]]
else:
    df_gather = None

def show_aggrid(df_to_show, height=400):
    gb = GridOptionsBuilder.from_dataframe(df_to_show)

    # Thêm cột STT – luôn giữ đúng số dòng hiển thị bất kể sắp xếp/lọc
    gb.configure_column("STT", header_name="STT", valueGetter="node.rowIndex + 1", width=70, pinned="left", sortable=False)

    for col in df_to_show.columns:
        if col == "ID":
            gb.configure_column("ID", width=90, cellStyle={'textAlign': 'left'})
        elif col == "Name":
            gb.configure_column("Name", width=160)
        elif df_to_show[col].dtype.kind in 'iuf':
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
df_general.insert(0, "STT", None)
show_aggrid(df_general)

st.subheader("🪙 Tài nguyên đã tiêu")
df_resources.insert(0, "STT", None)
show_aggrid(df_resources)

st.subheader("⚔️ Số lượng kill theo từng tier")
df_kills.insert(0, "STT", None)
show_aggrid(df_kills, height=500)

if df_gather is not None:
    st.subheader("⛏️ Tài nguyên đã thu thập")
    df_gather.insert(0, "STT", None)
    show_aggrid(df_gather, height=400)