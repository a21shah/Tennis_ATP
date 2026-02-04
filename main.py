import polars as pl
import points_dict
from tournament_dict import tournaments
import sys
sys.stdout.reconfigure(encoding='utf-8')

# read file
file_2024 = 'atp_matches_2024.csv'
df = pl.read_csv(file_2024, infer_schema_length=None)
print(df.shape) # (3076, 49)

keep_cols = ['tourney_name', 'surface', 'draw_size', 'tourney_level', 'tourney_date', 'winner_id', 'winner_name', 'winner_seed', 'loser_id', 'loser_name', 'loser_seed', 'round']
winner_cols_rename = {'winner_id':'player_id', 'winner_name':'player_name', 'winner_seed':'player_seed'} 
non_winner_cols_rename = {'loser_id':'player_id', 'loser_name':'player_name', 'loser_seed':'player_seed'}

draw_size = {96:128, 56:64}
exclude_tournaments = ['United Cup', 'Laver Cup', 'Next Gen Finals']

df1 = df[keep_cols].clone()
df1 = df1.with_columns(pl.col('draw_size').replace(draw_size).alias('draw_size'))
df1 = df1.filter((pl.col('tourney_level').is_in(['A', 'M', 'G', 'F'])) & (~pl.col('tourney_name').is_in(exclude_tournaments)))

print(df1.shape)

def get_points(df, tourney_level, draw_size, points_dict):
    
    df_filter = df.filter((pl.col('tourney_level') == tourney_level) & (pl.col('draw_size') == draw_size))

    df_non_winner = df_filter.with_columns(pl.col('round').replace_strict(points_dict, default=None).alias('points'))
    df_non_winner = df_non_winner[['tourney_name','tourney_level','loser_id','loser_name','loser_seed','round','points']].rename(non_winner_cols_rename)

    df_winner = (
        df_filter
        .filter(pl.col('round') == 'F')
        .with_columns([
            pl.lit('W').alias('round'),
            pl.lit(points_dict['W']).alias('points')
        ])
    )

    df_winner = df_winner[['tourney_name','tourney_level','winner_id','winner_name','winner_seed','round','points']].rename(winner_cols_rename)
    df_winner

    df_non_winner = df_non_winner.with_columns(pl.col('points').cast(pl.Int32))
    df_points = pl.concat([df_non_winner, df_winner])
    df_points

    return df_points

def assign_points_second_round_seeded_losers(df, points_df, tourney_level, draw_size, second_round, points_dict):

    all_matches = df.filter((pl.col('tourney_level') == tourney_level) & (pl.col('draw_size') == draw_size))

    # Count matches per player per tournament
    player_match_count = (
        all_matches
        .with_columns([
            pl.col('loser_id').alias('player_id_loser'),
            pl.col('winner_id').alias('player_id_winner')
        ])
        .unpivot(index=['tourney_name', 'tourney_date'], on=['player_id_loser', 'player_id_winner'], variable_name='role', value_name='player_id')
        .group_by(['tourney_name', 'tourney_date', 'player_id'])
        .agg(pl.len().alias('match_count'))
    )

    # Get players with a loss in the second round that have only played 1 match
    second_round_bye_losers = (
        all_matches
        .filter(pl.col('round') == second_round)
        .select(['tourney_name', 'tourney_date', 'loser_id', 'loser_name'])
        .rename({'loser_id': 'player_id', 'loser_name': 'player_name'})
        .join(player_match_count, on=['tourney_name', 'tourney_date', 'player_id'], how='inner')
        .filter(pl.col('match_count') == 1)
    )

    second_round_bye_losers = second_round_bye_losers.with_columns((pl.lit(points_dict).alias('points')), (pl.lit(second_round).alias('round')))

    points_df = (
        points_df.join(second_round_bye_losers, on=['tourney_name', 'player_id', 'player_name', 'round'], how='left')
        .with_columns(pl.coalesce(['points_right', 'points']).alias('points'))
        #.drop('points_right')
    )

    return points_df

def pivot_df(df):
    
    df = df.pivot(
        values = "points",
        index = ["player_id", "player_name"],
        on = ["tourney_name", "tourney_level"],
        aggregate_function="first"
    )

    return df

### Grand Slams ###

df_gs = get_points(df1, 'G', 128, points_dict.points_GS)
df_gs_points = pivot_df(df_gs)
df_gs_points

### ATP Masters ###

# 96 Player Draw
df_masters_96 = get_points(df1, 'M', 128, points_dict.points_1000_96)
# Players that received a bye in R64 in a 48 Player Draw and lost get 10 points
df_masters_96 = assign_points_second_round_seeded_losers(df1, df_masters_96, 'M', 128, 'R64', points_dict.points_1000_96['R128'])
df_masters_96_points = pivot_df(df_masters_96)

# 56 Player Draw
df_masters_56 = get_points(df1, 'M', 64, points_dict.points_1000_56)
# Players that received a bye in R32 in a 48 Player Draw and lost get 10 points
df_masters_56 = assign_points_second_round_seeded_losers(df1, df_masters_56, 'M', 64, 'R32', points_dict.points_1000_56['R64'])
df_masters_56_points = pivot_df(df_masters_56)

### Map 250 and 500 level tournaments ###
df_atp = df1.filter((pl.col('tourney_level')=='A'))

df_atp = df_atp.with_columns(pl.col("tourney_name").replace_strict(tournaments).alias('tourney_info'))

df_atp = df_atp.with_columns(
    pl.col("tourney_info").list.get(0).alias("tourney_level"),
    pl.col("tourney_info").list.get(1).alias("tourney_name")
)

### ATP 500 ###

# 32 Player Draw
df_500_32 = get_points(df_atp, '500', 32, points_dict.points_500_32)
df_500_32_points = pivot_df(df_500_32)

# 48 Player Draw
df_500_48 = get_points(df_atp, '500', 64, points_dict.points_500_48)
# Players that received a bye in R32 in a 48 Player Draw and lost get 0 points
df_500_48 = assign_points_second_round_seeded_losers(df_atp, df_500_48, '500', 64, 'R32', points_dict.points_500_48['R64'])
df_500_48_points = pivot_df(df_500_48)

### ATP 250 ###

# 32 Draw
df_250_32 = get_points(df_atp, '250', 32, points_dict.points_250_32)
df_250_32_points = pivot_df(df_250_32)

# 48 Draw
df_250_48 = get_points(df_atp, '250', 64, points_dict.points_250_48)
# Players that received a bye in R32 in a 48 Player Draw and lost get 0 points
df_250_48 = assign_points_second_round_seeded_losers(df_atp, df_250_48, '250', 64, 'R32', points_dict.points_250_48['R64'])
df_250_48_points = pivot_df(df_250_48)

# 28 Draw
df_250_28 = get_points(df_atp, '250', 28, points_dict.points_250_32)
# Players that received a bye in R16 in a 28 Player Draw and lost get 0 points
df_250_28 = assign_points_second_round_seeded_losers(df_atp, df_250_28, '250', 28, 'R16', points_dict.points_250_32['R32'])
df_250_28_points = pivot_df(df_250_28)

### ATP Finals ###
df_atp_finals = df1.filter((pl.col('tourney_name') == 'Tour Finals'))
df_atp_finals = df_atp_finals.with_columns(pl.col('round').replace_strict(points_dict.points_ATP_Finals, default=None).alias('points'))
df_atp_finals = df_atp_finals[['tourney_name','tourney_level','winner_id','winner_name','winner_seed','points']].rename(winner_cols_rename)
df_atp_finals = df_atp_finals.group_by(['tourney_name','tourney_level','player_id', 'player_name']).agg(pl.col('points').sum().alias('points'))
df_atp_finals_points = pivot_df(df_atp_finals)
df_atp_finals_points

### List of all Players who played in the 2024 ATP Tour ###
del winner_cols_rename['winner_seed']
del non_winner_cols_rename['loser_seed']

winners = df1[['winner_id', 'winner_name',]].unique().rename(winner_cols_rename)
losers = df1[['loser_id', 'loser_name', ]].unique().rename(non_winner_cols_rename)
players = pl.concat([winners, losers])

### Combine all the Tournaments ###
final_atp_points_df = (
    players.join(df_gs_points, on=['player_id', 'player_name'], how='left')
    .join(df_masters_96_points, on=['player_id', 'player_name'], how='left')
    .join(df_masters_56_points, on=['player_id', 'player_name'], how='left')
    .join(df_500_32_points, on=['player_id', 'player_name'], how='left')
    .join(df_500_48_points, on=['player_id', 'player_name'], how='left')
    .join(df_250_32_points, on=['player_id', 'player_name'], how='left')
    .join(df_250_48_points, on=['player_id', 'player_name'], how='left')
    .join(df_250_28_points, on=['player_id', 'player_name'], how='left')
    .join(df_atp_finals_points, on=['player_id', 'player_name'], how='left')
)
