import json
import polars as pl
import streamlit as st

@st.cache_data
def load_atp_points(year):
    file = f'atp_points/points_{year}.csv'
    
    return pl.read_csv(file, infer_schema_length=None)

@st.cache_data
def tournament_level_map(df):
    with open(f'atp_tournaments/tournaments_{year}.json', 'r') as file:
        data = json.load(file)
    
    return data

year = 2025
st.set_page_config(layout='wide')
st.title(f'ATP Points to Defend {year}')
   
df = load_atp_points(year)
df.drop_in_place('player_id')
tournament_map = tournament_level_map(df)

players = st.sidebar.multiselect(
    'Players',
    options=(df['player_name'].unique(maintain_order=True)),
    default=[]
)

tournament_levels = st.sidebar.multiselect(
    'Tournament Level',
    options=sorted(list(tournament_map.keys())),
    default=[]
)

player_col = ['player_name']
filter_tournaments = []

if tournament_levels:
    for selected_tournament in tournament_levels:
        filter_tournaments.extend(tournament_map[selected_tournament])


if filter_tournaments:
    options = st.sidebar.multiselect('Tournaments', options=filter_tournaments)
    if options:
        cols = player_col + options
    else:
        cols = player_col + filter_tournaments
    df = df.select(cols)

if players:
    df = df.filter(pl.col("player_name").is_in(players))
    df = df[[s.name for s in df if not (s.null_count() == df.height)]]

st.dataframe(df, width='stretch')




