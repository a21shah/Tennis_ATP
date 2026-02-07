import streamlit as st
import polars as pl

# read file
year = 2025
file = f'atp_points/points_{year}.csv'
df = pl.read_csv(file, infer_schema_length=None)

st.set_page_config(layout="wide")
st.title(f'ATP Points to Defend {year}')
st.dataframe(df, width='stretch')#, width='stretch', hide_index=True)
