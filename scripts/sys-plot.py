# %% imports
import csv
import matplotlib.pyplot as plt
from typing import List, Tuple, Dict, Any, Set
from pathlib import Path

# %% functions
class StatsData:
  def __init__(self, data: Tuple[
        List[Tuple[int, str]],
        Dict[int, str],
        Dict[int, List[Tuple[int, float, float]]],
        List[Dict[str, Any]],
        Set[int],
        int
    ], name: str = ''):
    self.events = data[0]
    self.pidmap = data[1]
    self.stats = data[2]
    self.latency = data[3]
    self.pIds = data[4]
    self.fts = data[5]
    self.name = name

def getTs(ts, firstTimeStamp = 0):
  return float(ts - firstTimeStamp) / 1000

def getEventColorAndStyle(name):
  if name == 'KILLED': return ('r', '--')
  if name == 'STARTED': return ('g', '-.')
  return ('g', '-')

def getEvent(folder: Path):
  with open(folder / 'events.csv') as f:
    events = [ (int(ts), name) for ts, name in csv.reader(f.readlines())]
    return events

def getPidmap(folder: Path):
  with open(folder / 'pidMap.csv') as f:
    lines = f.readlines()
    pidmap: Dict[int, str] = {}
    for l in lines:
      pid, name = l.split(',')
      pidmap[int(pid)] = name.strip('\n')
    return pidmap

def getStats(folder: Path):
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

def getLatency(folder: Path):
  data = []
  with open(folder / 'sink.csv', 'r') as f:
      for line in f:
          [ _, workername, cnt, id, ts, txts, rxts, latency, bytes, latencies, processorId, shish ] = line.split(',')
          latencies = [ int(l) for l in latencies.split('|') ]
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
  start = data[0]['txts']
  for d in data:
    d['ts'] = d['txts'] - start
  return (data, pIds)

def loadEverything(folderName: str, name: str | None = None):
  folder = Path('../results/') / folderName
  events = getEvent(folder)
  pidmap = getPidmap(folder)
  stats = getStats(folder)
  latency, pIds = getLatency(folder)
  firstTimeStamp = [ s[0] for s in stats[list(stats.keys())[0]] ][0]

  return StatsData( (events, pidmap, stats, latency, pIds, firstTimeStamp), name if name is not None else folderName)

# %% plots functions
def plotCpuMem(datas: List[StatsData]):
  fig, (axCpu, axMem) = plt.subplots(2, 1, figsize=(8, 7))

  for data in datas:
    tss = [ s[0] for s in data.stats[ list(data.stats.keys())[0] ] ]
    interval = tss[1] - tss[0]
    timestamp = [ getTs(s - (interval / 2), data.fts) for s in tss ]

    cpu = {}
    mem = {}
    for pid in data.stats:
      cpu[pid] = [ s[1] for s in data.stats[pid] ]
      mem[pid] = [ s[2] / 1000000 for s in data.stats[pid] ]

    stacksCpu = axCpu.stackplot(timestamp, cpu.values(), labels=[ data.pidmap[pid] for pid in data.stats ])
    stacksMem = axMem.stackplot(timestamp, mem.values(), labels=[ data.pidmap[pid] for pid in data.stats ])

    hatches=["\\", "//","+"]
    for stacks in [stacksCpu, stacksMem]:
      for i, stack in enumerate(stacks):
        stack.set_hatch(hatches[i % len(hatches)])


  axCpu.set_ylabel('cpu usage [% a of core]')
  axMem.set_ylabel('mem usage [MB]')
  axMem.set_xlabel('time [s]')

  axCpu.set_ylim(0, 800)
  axMem.set_ylim(0, 1600)
  handles, labels = axCpu.get_legend_handles_labels()
  axCpu.legend(handles[::-1], labels[::-1], loc='upper left')


  if len(datas) == 1:
    data = datas[0]
    for ax in [axCpu, axMem]:
      for ts, name in data.events:
        color, style = getEventColorAndStyle(name)
        ax.axvline(x=getTs(ts, data.fts), color=color, linestyle=style)
    
  plt.show()

def plotLatency(datas: List[StatsData], ylim: int | None = None, sameColor = False,):
  colors = [ f"C{i}" for i in range(10) ]
  for data in datas:
    x = [ getTs(d['ts']) for d in data.latency ]

    pidFilter = [ d['processorId'] for d in data.latency ]
    lat =       [ d['latency'] for d in data.latency ]
    # lat1 =      [ d['latencies'][-2] for d in data.latency ]
    # lat2 =      [ d['latencies'][-1] for d in data.latency ]

    for pId in data.pIds:
      color = colors[0] if sameColor else colors.pop(0)
      y = [ v if p == pId else None for v, p in zip(lat, pidFilter) ]
      plt.plot(x, y, label=f'{data.name} Id:{pId}', color=color)

  if len(datas) == 1:
    data = datas[0]
    for ts, name in data.events:
      if name == 'KILLED':
        color, style = getEventColorAndStyle(name)
        plt.axvline(x=getTs(ts, data.fts), color=color, linestyle=style)

  plt.xlabel('time [s]')
  plt.ylabel('latency [ms]')
  if ylim is not None:
    plt.ylim(0, ylim)
  plt.legend()
  plt.show()

def plotItemsPerSecond(datas: List[StatsData], ylim: int | None = None):
  for data in datas:
    tss = [ d['ts'] for d in data.latency ]
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

    for ts, name in data.events:
      if name == 'KILLED':
        color, style = getEventColorAndStyle(name)
        plt.axvline(x=getTs(ts, data.fts), color=color, linestyle=style)
    plt.plot([getTs(ts + (wLen/2), data.fts) for ts in tsRange], speed, label=data.name)
  plt.xlabel('time [s]')
  plt.ylabel('throughput [items/s]')
  if ylim is not None:
    plt.ylim(0, ylim)
  plt.legend()
  plt.show()

# %% load
data = loadEverything('000_FPS_NOKILL_T20000_R2_L1_Qsrc100_Q100')

# %% plotta
plotCpuMem([data])
plotLatency([data], ylim=500)
plotItemsPerSecond([data], ylim=4000)


# %%
