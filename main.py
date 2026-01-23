import polars as pl

df = pl.read_csv('atp_tennis.csv', infer_schema_length=None)

print(df.shape)

