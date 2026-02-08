import polars as pl
import points_dict

winner_cols_rename = {'winner_id':'player_id', 'winner_name':'player_name', 'winner_seed':'player_seed'} 
non_winner_cols_rename = {'loser_id':'player_id', 'loser_name':'player_name', 'loser_seed':'player_seed'}


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
    
    df = df.with_columns(pl.concat_str([pl.col('points'), pl.col('round')], separator=' - ').alias('points_round'))
    
    df = df.pivot(
        values = 'points',
        index = ['player_id', 'player_name'],
        on = ['tourney_name', 'tourney_level'],
        aggregate_function='first'
    )

    return df