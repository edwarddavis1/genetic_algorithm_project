import pandas as pd

df = pd.DataFrame(columns={'A', 'B'})
new_row = {'A': 12, 'Bw': "ten"}
df.append(new_row, ignore_index=True)
df
len(df)
