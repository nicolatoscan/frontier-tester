# %% import
import csv
import matplotlib.pyplot as plt
from typing import List, Tuple, Dict
from pathlib import Path
import numpy as np
# %% load
def loadEverything(folderName: str):
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
        pidmap[int(pid)] = name.strip('\n')
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

  def getLatency():
    data = []
    with open(folder / 'sink.csv', 'r') as f:
        for line in f:
            [ _, workername, cnt, id, ts, txts, rxts, latency, bytes, latencies, processorId, shish ] = line.split(',')
            data.append({
                "Workername": workername,
                "cnt": int(cnt),
                "id": int(id),
                "ts": int(ts),
                "txts": int(txts),
                "rxts": int(rxts),
                "latency": int(latency),
                "bytes": int(bytes),
                "latencies": latencies,
                "processorId": processorId,
            })
    pIds = set( [ d['processorId'] for d in data ] )
    data[0]['diff'] = 0
    for i in range(1, len(data)):
        data[i]['diff'] = data[i]['rxts'] - data[i-1]['rxts']
    return (data, pIds)

  events = getEvent()
  pidmap = getPidmap()
  stats = getStats()
  latency, pIds = getLatency()
  firstTimeStamp = [ s[0] for s in stats[list(stats.keys())[0]] ][0]

  return (events, pidmap, stats, latency, pIds, firstTimeStamp)

def getTs(ts):
  return float(ts - firstTimeStamp) / 1000
def getEventColorAndStyle(name):
  if name == 'KILLED':
    return ('r', '--')
  return ('g', '-')
# firstTimeStamp = [ e for e in events if e[1] == 'STARTED' ][0][0]

events, pidmap, stats, latency, pIds, firstTimeStamp = loadEverything('FREE_KILL_T20000_R3_L1_Qsrc100_Q100')

# %% plot cpu usage per pid
def plotUsagePerPid(ax: plt.Axes, pid: int, useCpu = True):
  timestamp = [ getTs(s[0]) for s in stats[pid] ]
  # timestamp = [ t for t in timestamp ]
  y = [ s[1 if useCpu else 2] for s in stats[pid] ]
  if not useCpu:
    y = [ v / 1000000 for v in y ]
  ax.plot(timestamp, y)
  if not useCpu:
    ax.set_xlabel('timestamp [s]')
  ax.set_ylabel('cpu usage [%]' if useCpu else 'mem usage [MB]')
  if useCpu:
    ax.set_ylim(0, 100)
  else:
    ax.set_ylim(0, 500)
  for ts, name in events:
    color, style = getEventColorAndStyle(name)
    ax.axvline(x=getTs(ts), color=color, linestyle=style, label=name)
  if useCpu:
    ax.legend()
prNr = 1
def plotCpuMemPerPid(pid: int):
  global prNr
  fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 5))
  plotUsagePerPid(ax1, pid, True)
  plotUsagePerPid(ax2, pid, False)
  name = pidmap[pid]
  if name.strip('\n') == 'PROCESSOR':
    name = 'WORKER ' + str(prNr)
    prNr += 1
  fig.suptitle(name)
  fig.show()
for pid in stats:
  plotCpuMemPerPid(pid)

# %% plot fun
def plot(attrib: str, ylim = False):
  x = [ getTs(d['rxts']) for d in latency ]
  # x = [ d['cnt'] for d in latency ]
  # plt.plot( [ d[attrib] for d in data ], x )
  # plt.show()
  # print([ d[attrib] for d in data ])
  for i, pId in enumerate(pIds):
    y = [ d[attrib] if d['processorId'] == pId else None for d in latency ]
    y2 = [ int(d['latencies'].split('|')[-2]) if d['processorId'] == pId else None for d in latency ]
    y1 = [ int(d['latencies'].split('|')[-1]) if d['processorId'] == pId else None for d in latency ]
    plt.plot(x, y1, label=f'Id1:{pId}')
    plt.plot(x, [ None if v1 is None or v2 is None else v1+v2 for v1, v2 in zip(y1,y2)], label=f'Id2:{pId}')

  for ts, name in events:
    if name == 'KILLED':
      color, style = getEventColorAndStyle(name)
      plt.axvline(x=getTs(ts), color=color, linestyle=style, label=name)
  # add labels
  plt.xlabel('timestamp [s]')
  plt.ylabel('latency [ms]')
  plt.title(attrib)
  if ylim:
    plt.ylim(0, 100)
  plt.legend()
  # plt.rcParams['figure.figsize'] = [8, 12]

  plt.show()

plot('latency', True)
# plot('socketLatency')
# plot('opLatency')
# %%
# plot item per seconds from timestamp list
def plotItemsPerSecond():
  tss = [ d['rxts'] for d in latency ]
  window = []
  speed = []
  wLen = 100
  tsRange = range(tss[0], tss[-1], wLen)
  for ts in tsRange:
    while len(tss) > 0 and tss[0] < ts + wLen:
      window.append(tss.pop(0))
    while len(window) > 0 and window[0] < ts:
      window.pop(0)
    speed.append(len(window) * (1000 / wLen))

  for ts, name in events:
    if name == 'KILLED':
      color, style = getEventColorAndStyle(name)
      plt.axvline(x=getTs(ts), color=color, linestyle=style, label=name)
  plt.plot([getTs(ts + (wLen/2)) for ts in tsRange], speed)
plotItemsPerSecond()
# %%
