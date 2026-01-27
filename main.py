import polars as pl

df = pl.read_csv('atp_matches_2024.csv', infer_schema_length=None)

print(df.shape)


