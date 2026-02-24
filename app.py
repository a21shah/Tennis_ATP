import json
import polars as pl
import streamlit as st

@st.cache_data
def load_atp_points(year):
    file = f'atp_points/points_{year}.csv'
    df = pl.read_csv(file, infer_schema_length=None)
    df = df.drop(['player_id', 'total_points_earned'])
    return df

@st.cache_data
def tournament_level_map():
    with open(f'atp_tournaments/tournaments_{year}.json', 'r') as file:
        return json.load(file)

@st.cache_data
def max_points(tournaments_json):
    points_max = {
        'ATP 250': 250,
        'ATP 500': 500,
        'Masters 1000': 1000,
        'Grand Slam': 2000,
        'ATP Finals': 1500
    }

    tournaments_max_dict = {}
    for level, tournaments in tournaments_json.items():
        for tournament in tournaments:
            tournaments_max_dict[tournament] = points_max[level]

    return tournaments_max_dict

    
year = 2025
st.set_page_config(layout='wide')
st.title(f'ATP Points to Defend {year}')
st.caption('Filter players and tournaments to explore points being defended')
   
df = load_atp_points(year)

tournament_map = tournament_level_map()

with st.sidebar:
    st.header('Filters')

    players = st.multiselect(
        'Players',
        options=df['player_name'].unique(maintain_order=True),
        key = 'players_filter'
    )

    st.divider()

    tournament_levels = st.multiselect(
        'Tournament Level',
        options=sorted(list(tournament_map.keys())),
        key = 'levels_filter'
    )

# Add to list all the tournaments available for all selected levels
levels = []
for level in tournament_levels:
    levels.extend(tournament_map[level])

all_tournaments = df.select(pl.exclude('player_name')).columns

if levels:
    available_tournaments = levels
else:
    available_tournaments = all_tournaments

with st.sidebar:
    st.caption(f'{len(available_tournaments)} tournaments available')

    selected_tournaments = st.multiselect(
        'Tournaments',
        options=available_tournaments,
        key = 'tournament_filter'
    )

    # Show checkbox only when tournaments selected
    drop_null_rows = False
    if selected_tournaments or tournament_levels:
        drop_null_rows = st.checkbox('Hide players with no results in selected tournaments', key = 'drop_nulls_filter')
       
    st.divider()

# ---------------- Filtering ---------------- #

player_name = ['player_name']

if selected_tournaments:
    cols = player_name + selected_tournaments
elif levels:
    cols = player_name + levels
else:
    cols = df.columns

df = df.select(cols)

if players:
    df = df.filter(pl.col('player_name').is_in(players))

if drop_null_rows:
    df = df.filter(~pl.all_horizontal(pl.all().exclude(player_name).is_null()))

# Remove columns that are entirely null
df = df[[s.name for s in df if not (s.null_count() == df.height)]]

# ---------------- Dashboard Info ---------------- #

metric1, metric2, metric3 = st.columns(3)

metric1.metric('Players Shown', df.select(pl.col('player_name').n_unique()))

metric2.metric('Tournaments Displayed', df.width - 1)

if tournament_levels or selected_tournaments or players:
    max_points_available = 0

    tournament_max_points_dict = max_points(tournament_map)
    for final_cols in df.columns[1:]:
        print(tournament_max_points_dict[final_cols])
        max_points_available += tournament_max_points_dict[final_cols]

    metric3.metric('Maximum Points Available across selected Tournaments', max_points_available)


# Active filters summary
active_filters = []

if players:
    active_filters.append(f'{len(players)} players')

if tournament_levels:
    active_filters.append(f'{len(tournament_levels)} levels')

if selected_tournaments:
    active_filters.append(f'{len(selected_tournaments)} tournaments')

if active_filters:
    st.caption('Active filters: ' + ', '.join(active_filters))


# ---------------- Results ---------------- #

st.subheader('Results')

if df.width > 1:
    df = df.with_columns(
        pl.sum_horizontal(
            pl.all()
            .exclude(player_name)
            .cast(pl.Utf8, strict=False)
            .str.extract(r'(\d+)', 1)
            .cast(pl.Int64)
        )
        .alias('cumulative_points')
    )

st.dataframe(df, width='stretch')
