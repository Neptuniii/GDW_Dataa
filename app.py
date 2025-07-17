import streamlit as st
import pandas as pd

# Load dữ liệu
df = pd.read_csv("naphaluancod_2025-07-16.csv", usecols=[
    'governor_id', 'governor_name', 'historical_highest_power',
    'units_killed', 'units_dead', 'units_healed',  # <-- thêm 2 dòng này nếu bị thiếu
    'gold_spent', 'wood_spent', 'stone_spent', 'mana_spent', 'gems_spent',
    'tier_1_kills', 'tier_2_kills', 'tier_3_kills', 'tier_4_kills', 'tier_5_kills',
])


# Đổi tên cột
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

# Tính % kill theo từng tier / tổng
for tier in ['T1', 'T2', 'T3', 'T4', 'T5']:
    kill_col = f"{tier} kill"
    pct_col = f"{tier}/Total"
    df[pct_col] = (df[kill_col] / df['Total kill'].replace(0, pd.NA)) * 100
    df[pct_col] = df[pct_col].map(lambda x: f"{x:.2f}%" if pd.notnull(x) else "0.00%")

# Sắp xếp lại thứ tự cột: kill -> % tương ứng
cols_order = ['ID', 'Name', 'Highest Power', 'Total kill', 'Total dead', 'Total healed']
for tier in ['T1', 'T2', 'T3', 'T4', 'T5']:
    cols_order.append(f"{tier} kill")
    cols_order.append(f"{tier}/Total")
cols_order += ['Gold spent', 'Wood spent', 'Stone spent', 'Mana spent', 'Gem spent']
df = df[cols_order]

# Giao diện Streamlit
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

df_general = filtered_df[general_cols]
df_resources = filtered_df[['ID', 'Name'] + resource_cols]
kill_cols_ordered = []
for tier in ['T1', 'T2', 'T3', 'T4', 'T5']:
    kill_cols_ordered.append(f"{tier} kill")
    kill_cols_ordered.append(f"{tier}/Total")

# Tạo bảng 3
df_kills = filtered_df[['ID', 'Name', 'Total kill'] + kill_cols_ordered]

# 📊 Hiển thị từng bảng
st.subheader("🧮 Thông tin cơ bản")
st.dataframe(df_general, use_container_width=True)

st.subheader("🪙 Tài nguyên đã tiêu")
st.dataframe(df_resources, use_container_width=True)

st.subheader("⚔️ Số lượng kill theo từng tier")
st.dataframe(df_kills, use_container_width=True)

