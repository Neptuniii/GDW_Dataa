import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder
import matplotlib.pyplot as plt

df = pd.read_csv("naphaluancod_2025-07-16.csv", usecols=[
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

st.set_page_config(layout="wide")
st.title("GDW Data – Latest Update: 16/7/2025")
st.title("By Neptuniii")

search = st.text_input("Tìm theo ID hoặc Tên:")
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
    from st_aggrid import GridOptionsBuilder, AgGrid
    from streamlit import markdown

    gb = GridOptionsBuilder.from_dataframe(df_to_show)

    for col in df_to_show.columns:
        if col == "ID":
            gb.configure_column(col, width=90, cellStyle={'textAlign': 'left'})
        elif col == "Name":
            gb.configure_column(col, width=180)
        elif col == "Highest Power":
            gb.configure_column(col, width=140, type=["numericColumn", "numberColumnFilter"],
                                valueFormatter="x.toLocaleString()")
        elif col == "Total kill":
            gb.configure_column(col, width=140, type=["numericColumn", "numberColumnFilter"],
                                valueFormatter="x.toLocaleString()")
        elif col == "Total dead":
            gb.configure_column(col, width=130, type=["numericColumn", "numberColumnFilter"],
                                valueFormatter="x.toLocaleString()")
        elif col == "Total healed":
            gb.configure_column(col, width=130, type=["numericColumn", "numberColumnFilter"],
                                valueFormatter="x.toLocaleString()")
        elif col == "Gold spent":
            gb.configure_column(col, width=130, type=["numericColumn", "numberColumnFilter"],
                                valueFormatter="x.toLocaleString()")
        elif col == "Wood spent":
            gb.configure_column(col, width=130, type=["numericColumn", "numberColumnFilter"],
                                valueFormatter="x.toLocaleString()")
        elif col == "Stone spent":
            gb.configure_column(col, width=130, type=["numericColumn", "numberColumnFilter"],
                                valueFormatter="x.toLocaleString()")
        elif col == "Mana spent":
            gb.configure_column(col, width=130, type=["numericColumn", "numberColumnFilter"],
                                valueFormatter="x.toLocaleString()")
        elif col == "Gem spent":
            gb.configure_column(col, width=120, type=["numericColumn", "numberColumnFilter"],
                                valueFormatter="x.toLocaleString()")
        elif col in ["T1 kill", "T2 kill", "T3 kill", "T4 kill", "T5 kill"]:
            gb.configure_column(col, width=110, type=["numericColumn", "numberColumnFilter"],
                                valueFormatter="x.toLocaleString()")
        elif "/Total (%)" in col:
            gb.configure_column(col, width=115,
                                type=["numericColumn", "numberColumnFilter", "customNumericFormat"],
                                precision=2,
                                valueFormatter="x.toFixed(2) + '%'")
        else:
            gb.configure_column(col, width=120)

    gridOptions = gb.build()

    # 💡 Bọc AgGrid trong thẻ div scroll ngang
    st.markdown("""
        <div style='overflow-x: auto;'>
    """, unsafe_allow_html=True)

    AgGrid(
        df_to_show,
        gridOptions=gridOptions,
        height=height,
        fit_columns_on_grid_load=True,
        use_container_width=False,  # ⚠️ Cực kỳ quan trọng: Không ép vừa container
        allow_unsafe_jscode=True,
        theme="streamlit"
    )

    st.markdown("</div>", unsafe_allow_html=True)



st.subheader("🧮 Thông tin cơ bản")
show_aggrid(df_general)

st.subheader("🪙 Tài nguyên đã tiêu")
show_aggrid(df_resources)

st.subheader("⚔️ Số lượng kill theo từng tier")
show_aggrid(df_kills, height=500)
