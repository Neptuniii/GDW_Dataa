import streamlit as st
import pandas as pd

st.markdown("""
    <style>
        .css-1d391kg {  /* class của table cell */
            font-size: 20px !important;
        }
        .css-1v0mbdj {  /* class của table header */
            font-size: 20px !important;
        }
    </style>
""", unsafe_allow_html=True)

df = pd.read_csv("naphaluancod_2025-07-16.csv", usecols=[
    'governor_id', 'governor_name', 'power', 'units_killed', 'tier_1_kills', 'tier_2_kills', 'tier_3_kills', 'tier_4_kills', 'tier_5_kills', 'gold_spent', 'wood_spent', 'stone_spent', 'mana_spent', 'gems_spent'
])

df = df.rename(columns={
    'governor_id': 'ID',
    'governor_name': 'Name',
    'power': 'Power',
    'kill_points': 'Kill point',
    'units_killed': 'Total kill',
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

st.set_page_config(layout="wide")
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

st.dataframe(filtered_df, height=800, use_container_width=True)



