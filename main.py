import polars as pl
import points_dict
import sys
sys.stdout.reconfigure(encoding='utf-8')

# read file
file_2024 = 'atp_matches_2024.csv'
df = pl.read_csv(file_2024, infer_schema_length=None)
print(df.shape) # (3076, 49)

winner_cols_rename = {'winner_id':'player_id', 'winner_name':'player_name',}# 'winner_seed':'player_seed'} 
non_winner_cols_rename = {'loser_id':'player_id', 'loser_name':'player_name'}#, 'loser_seed':'player_seed'}

keep_cols = ['tourney_name', 'surface', 'draw_size', 'tourney_level', 'tourney_date', 'winner_id', 'winner_name', 'winner_seed', 'loser_id', 'loser_name', 'loser_seed', 'round']
df1 = df[keep_cols].clone()

### Grand Slams ###
df_gs = df1.filter(pl.col('tourney_level')=='G')

df_gs_non_winner = df_gs.with_columns(pl.col("round").replace_strict(points_dict.points_GS, default=None).alias("points"))
df_gs_non_winner = df_gs_non_winner[['tourney_name','tourney_level','loser_id','loser_name','points']].rename(non_winner_cols_rename)

df_gs_winner = (
    df_gs
    .filter(pl.col('round') == 'F')
    .with_columns([
        pl.lit('W').alias('round'),
        pl.lit(points_dict.points_GS['W']).alias('points')
    ])
)
df_gs_winner = df_gs_winner[['tourney_name','tourney_level','winner_id','winner_name','points']].rename(winner_cols_rename)


df_gs_non_winner = df_gs_non_winner.with_columns(pl.col('points').cast(pl.Int32))
df_gs = pl.concat([df_gs_non_winner, df_gs_winner])
# print(df_gs.head(5))

df_gs = df_gs.pivot(
    values = "points",
    index = ["player_id", "player_name"],
    on = ["tourney_name", "tourney_level"],
    aggregate_function="first"
)

print(df_gs.filter(pl.col("player_name") == "Carlos Alcaraz"))