# %% import
import csv
import pandas as pd
import matplotlib.pyplot as plt

# %% load
with open('../results/cpu.csv') as f:
  lines = [c for c in csv.reader(f.readlines()[5:])]
  df = pd.DataFrame(lines[1:], columns=lines[0], dtype=float)

# %%
# plot cpu
df[ [ f'cpu{i} usage:usr' for i in range(11) ] ].plot(title='CPU',  ylim=(0, 100))


# %% plot mem
df['used'].plot(title='Memory', ylim=(0, 7000000000))

# %%
