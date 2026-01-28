import polars as pl

file_2024 = 'atp_matches_2024.csv'

df = pl.read_csv(file_2024, infer_schema_length=None)

print(df.shape) # (3076, 49)


