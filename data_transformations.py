from functions import *
import os
import sys
sys.stdout.reconfigure(encoding='utf-8')

# read file
year = 2025
file = f'matches_data/atp_matches_{year}.csv'
df = pl.read_csv(file, infer_schema_length=None)
print(df.shape)

keep_cols = ['tourney_name', 'surface', 'draw_size', 'match_num', 'tourney_level', 'tourney_date', 'winner_id', 'winner_name', 'winner_seed', 'loser_id', 'loser_name', 'loser_seed', 'round']

df1 = df[keep_cols].clone()
tournament_levels = ['250', '500', 'M', 'G', 'F']
df1 = df1.filter((pl.col('tourney_level').is_in(tournament_levels)))
print(df1.shape)

### Grand Slams ###

df_gs = get_points(df1, 'G', 128, points_dict.points_GS)
df_gs_points = pivot_df(df_gs)
df_gs_points

### ATP Masters ###

# 96 Player Draw
df_masters_96 = get_points(df1, 'M', 96, points_dict.points_1000_96)
# Players that received a bye in R64 in a 48 Player Draw and lost get 10 points
df_masters_96 = assign_points_second_round_seeded_losers(df1, df_masters_96, 'M', 96, 'R64', points_dict.points_1000_96['R128'])
df_masters_96_points = pivot_df(df_masters_96)

# 56 Player Draw
df_masters_56 = get_points(df1, 'M', 56, points_dict.points_1000_56)
# Players that received a bye in R32 in a 48 Player Draw and lost get 10 points
df_masters_56 = assign_points_second_round_seeded_losers(df1, df_masters_56, 'M', 56, 'R32', points_dict.points_1000_56['R64'])
df_masters_56_points = pivot_df(df_masters_56)

### ATP 500 ###

# 32 Player Draw
df_500_32 = get_points(df1, '500', 32, points_dict.points_500_32)
df_500_32_points = pivot_df(df_500_32)

# 48 Player Draw
df_500_48 = get_points(df1, '500', 48, points_dict.points_500_48)
# Players that received a bye in R32 in a 48 Player Draw and lost get 0 points
df_500_48 = assign_points_second_round_seeded_losers(df1, df_500_48, '500', 48, 'R32', points_dict.points_500_48['R64'])
df_500_48_points = pivot_df(df_500_48)

### ATP 250 ###

# 32 Draw
df_250_32 = get_points(df1, '250', 32, points_dict.points_250_32)
df_250_32_points = pivot_df(df_250_32)

# 48 Draw
df_250_48 = get_points(df1, '250', 48, points_dict.points_250_48)
# Players that received a bye in R32 in a 48 Player Draw and lost get 0 points
df_250_48 = assign_points_second_round_seeded_losers(df1, df_250_48, '250', 48, 'R32', points_dict.points_250_48['R64'])
df_250_48_points = pivot_df(df_250_48)

# 28 Draw
df_250_28 = get_points(df1, '250', 28, points_dict.points_250_32)
# Players that received a bye in R16 in a 28 Player Draw and lost get 0 points
df_250_28 = assign_points_second_round_seeded_losers(df1, df_250_28, '250', 28, 'R16', points_dict.points_250_32['R32'])
df_250_28_points = pivot_df(df_250_28)

### ATP Finals ###

df_atp_finals = df1.filter((pl.col('tourney_name') == 'ATP Finals'))

# Used to map points for the players that lost in the SF and F
semifinalists = df_atp_finals[['loser_id', 'round']].filter(pl.col('round').is_in(['SF', 'F']))
atp_final4_dict = dict(semifinalists.iter_rows())

# If player wins 0 matches, they won't have any points mapped and thus would be excluded from the group_by
df_atp_finals_loser = df_atp_finals[['tourney_name','tourney_level','loser_id','loser_name','loser_seed']].rename(non_winner_cols_rename)
df_atp_finals_loser = df_atp_finals_loser.with_columns(pl.lit(0).cast(pl.Int64).alias('points'))

df_atp_finals = df_atp_finals.with_columns(pl.col('round').replace_strict(points_dict.points_ATP_Finals, default=None).alias('points'))
df_atp_finals_winner = df_atp_finals[['tourney_name','tourney_level','winner_id','winner_name','winner_seed','points']].rename(winner_cols_rename)
df_atp_finals = pl.concat([df_atp_finals_loser, df_atp_finals_winner])

df_atp_finals = df_atp_finals.group_by(['tourney_name','tourney_level','player_id','player_name']).agg(pl.col('points').sum().alias('points'))
# By default map every player to round = RR except for those that lost in SF and F
df_atp_finals = df_atp_finals.with_columns(pl.col('player_id').replace_strict(atp_final4_dict, default='RR').alias('round'))
# Player that won ATP Finals should have round = W and that player would have at least 1100 points
df_atp_finals = df_atp_finals.with_columns(
    pl.when(pl.col('points') >= 1100)
    .then(pl.lit('W'))
    .otherwise(pl.col('round'))
    .alias('round')
)

df_atp_finals_points = pivot_df(df_atp_finals)

### List of all Players who participated in that year's ATP Tour ###

winner_cols_rename = {'winner_id':'player_id', 'winner_name':'player_name'} 
loser_cols_rename = {'loser_id':'player_id', 'loser_name':'player_name'}

winners = df1[['winner_id', 'winner_name',]].unique().rename(winner_cols_rename)
losers = df1[['loser_id', 'loser_name', ]].unique().rename(loser_cols_rename)
players = pl.concat([winners, losers])
players = players.unique()

join_cols = ['player_id', 'player_name']

final_atp_points_df = (
    players.join(df_gs_points, on=join_cols, how='left')
    .join(df_masters_96_points, on=join_cols, how='left')
    .join(df_masters_56_points, on=join_cols, how='left')
    .join(df_500_32_points, on=join_cols, how='left')
    .join(df_500_48_points, on=join_cols, how='left')
    .join(df_250_32_points, on=join_cols, how='left')
    .join(df_250_48_points, on=join_cols, how='left')
    .join(df_250_28_points, on=join_cols, how='left')
    .join(df_atp_finals_points, on=join_cols, how='left')
)

# Sort final Dataframe by date of occurence of each tournament

tournaments = df1.filter(pl.col('match_num')==1)['tourney_name', 'tourney_date'].unique().sort(by=['tourney_date', 'tourney_name'])
tournaments = tournaments['tourney_name'].to_list()
cols_order = join_cols + tournaments
final_atp_points_df = final_atp_points_df[cols_order]

# Add total points each player earned throughtout the entire season
final_atp_points_sorted_df = final_atp_points_df.with_columns(
    pl.sum_horizontal(
        pl.all()
        .exclude(["player_id", "player_name"])
        .cast(pl.Utf8, strict=False)
        .str.extract(r"(\d+)", 1)
        .cast(pl.Int64)
    )
    .alias('total_points_earned')
).sort(by='total_points_earned', descending=True)

final_atp_points_sorted_df = final_atp_points_sorted_df.filter(pl.col('total_points_earned')>0)

### Write data to file

output_dir = 'atp_points'
output_filename = f'points_{year}.csv'
full_path = os.path.join(output_dir, output_filename)

# Ensure directory exists (create it if not)
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
    print(f'Created directory: {output_dir}')

# Write DataFrame to the specific folder
final_atp_points_sorted_df.write_csv(full_path)
print(f'Created file {output_filename}')
