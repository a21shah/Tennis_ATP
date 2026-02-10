import polars as pl
import streamlit as st

@st.cache_data
def load_atp_points(year):
    file = f'atp_points/points_{year}.csv'
    return pl.read_csv(file, infer_schema_length=None)

@st.cache_data
def tournament_level_map(df):
    file = f'matches_data/atp_matches_{year}.csv'
    df = pl.read_csv(file, infer_schema_length=None)
    tourney_levels = (
        df
        .select(['tourney_name', 'tourney_level'])
        .unique(maintain_order=True)
        .group_by('tourney_level', maintain_order=True)
        .agg(pl.col('tourney_name'))
    )
    tourney_levels_dict = dict(zip(tourney_levels["tourney_level"].to_list(), tourney_levels["tourney_name"].to_list()))
    return tourney_levels_dict

year = 2025
st.set_page_config(layout='wide')
st.title(f'ATP Points to Defend {year}')
   
df = load_atp_points(year)
df.drop_in_place('player_id')
tournament_map = tournament_level_map(df)

players = st.sidebar.multiselect(
    'Players',
    options=sorted(df['player_name'].unique()),
    default=[]
)

tournament_levels = st.sidebar.multiselect(
    'Tournament Type',
    options=['ATP 250', 'ATP 500', 'Masters 1000', 'Grand Slam', 'ATP Finals'],
    default=[]
)

player_col = ['player_name']
tournament_dict = {'ATP 250':'250', 'ATP 500':'500', 'Masters 1000':'M', 'Grand Slam':'G', 'ATP Finals':'F'}
selected_tournaments = []
filter_tournaments = []

if tournament_levels:
    for tournament in tournament_levels:
            selected_tournaments.append(tournament_dict[tournament])

    for selected_tournament in selected_tournaments:
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




