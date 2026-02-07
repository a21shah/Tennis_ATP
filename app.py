import polars as pl
import streamlit as st

year = 2025

st.set_page_config(layout="wide")
st.title(f'ATP Points to Defend {year}')

@st.cache_data
def load_csv(year):
    file = f'atp_points/points_{year}.csv'
    return pl.read_csv(file, infer_schema_length=None)

df = load_csv(year)

players = st.sidebar.multiselect(
    "Players",
    options=sorted(df["player_name"].unique()),
    default=[]
)

if players:
    filtered_df = df.filter(pl.col('player_name').is_in(players))
    filtered_df = filtered_df[[s.name for s in filtered_df if not (s.null_count() == filtered_df.height)]]
else:
    filtered_df = df 

st.dataframe(filtered_df, width='stretch')



