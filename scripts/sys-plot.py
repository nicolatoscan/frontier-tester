# %% import
git coimport csv
import matplotlib.pyplot as plt
from typing import List, Tuple, Dict
from pathlib import Path
# %% load
folderName = 'ciao'
folder = Path('../results/') / folderName

def getEvent():
  with open(folder / 'events.csv') as f:
    events = [ (int(ts), name) for ts, name in csv.reader(f.readlines())]
    return events
def getPidmap():
  with open(folder / 'pidMap.csv') as f:
    lines = f.readlines()
    pidmap: Dict[int, str] = {}
    for l in lines:
      pid, name = l.split(',')
      pidmap[int(pid)] = name
    return pidmap
def getStats():
  with open(folder / 'monitoring.csv') as f:
    lines = f.readlines()
    pids = [ int(l.split(',')[0]) for l in lines[0].split('\t')[1:] ]
    stats: Dict[int, List[Tuple[int, float, float]]] = { pid: [] for pid in pids }

    for l in lines:
      statsList = l.split('\t')
      timestamp = int(statsList[0])
      for s in statsList[1:]:
        pid, cpu, mem = s.split(',')
        stats[int(pid)].append( (timestamp, float(cpu), float(mem)) )
  return stats

events = getEvent()
pidmap = getPidmap()
stats = getStats()

# %% plot cpu usage per pid
def getEventColorAndStyle(name):
  if name == 'KILLED':
    return ('r', '--')
  return ('g', '-')


def plotUsagePerPid(ax: plt.Axes, pid: int, useCpu = True):
  timestamp = [ s[0] for s in stats[pid] ]
  y = [ s[1 if useCpu else 2] for s in stats[pid] ]
  if not useCpu:
    y = [ v / 1000000 for v in y ]
  ax.plot(timestamp, y)
  ax.set_xlabel('timestamp')
  ax.set_ylabel('cpu usage [%]' if useCpu else 'mem usage [MB]')
  if useCpu:
    ax.set_ylim(0, 100)
  else:
    ax.set_ylim(0, 320)
  for ts, name in events:
    color, style = getEventColorAndStyle(name)
    ax.axvline(x=ts, color=color, linestyle=style, label=name)
  if useCpu:
    ax.legend()

def plotCpuMemPerPid(pid: int):
  fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(6, 8))
  plotUsagePerPid(ax1, pid, True)
  plotUsagePerPid(ax2, pid, False)
  fig.suptitle(pidmap[pid])
  fig.show()

for pid in stats:
  plotCpuMemPerPid(pid)

# %%
