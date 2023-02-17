# %% import
import csv
import pandas as pd
import matplotlib.pyplot as plt
from typing import List, Tuple
# %% load

events: List[Tuple[int, str]] = []
with open('../results/events.csv') as f:
  events = [ (int(ts), name) for ts, name in csv.reader(f.readlines())]
with open('../results/monitoring.csv') as f:
  lines = [c for c in csv.reader(f.readlines())]
  df = pd.DataFrame(lines, columns=[
    'timestamp', 'mem', 'cpu0', 'cpu1', 'cpu2', 'cpu3', 'cpu4', 'cpu5', 'cpu6', 'cpu7', 'cpu8', 'cpu9', 'cpu10', 'cpu11', 'avg'
    ], dtype=float)

# %%
# plot cpu
def plot(col: str, ylim: int):
  plt.plot(df['timestamp'], df[col])
  plt.ylim=(0, ylim)
  for ts, name in events:
    plt.axvline(x = ts, color = 'r', label = name)
  plt.legend()
  plt.show()


# %% plot mem
plot('mem', 7000000000)
plot('cpu4', 1)
# %%
