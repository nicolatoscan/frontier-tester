# %% imports
import matplotlib.pyplot as plt
from pathlib import Path
import csv

# %% read result file
folderName = 'dump'
folder = Path('../results/') / folderName
headers = [ "Workername","cnt","id","ts","txts","rxts","latency","bytes","opLatency","socketLatency","processorId"]

data = []
with open(folder / 'sink.csv', 'r') as f:
    for line in f:
        [ _, workername, cnt, id, ts, txts, rxts, latency, bytes, opLatency, socketLatency, processorId, shish ] = line.split(',')
        data.append({
            "Workername": workername,
            "cnt": int(cnt),
            "id": int(id),
            "ts": int(ts),
            "txts": int(txts),
            "rxts": int(rxts),
            "latency": int(latency),
            "bytes": int(bytes),
            "opLatency": int(opLatency),
            "socketLatency": int(socketLatency),
            "processorId": int(processorId),
        })
pIds = set( [ d['processorId'] for d in data ] )
data[0]['diff'] = 0
for i in range(1, len(data)):
    data[i]['diff'] = data[i]['rxts'] - data[i-1]['rxts']


def getEvent():
  with open(folder / 'events.csv') as f:
    events = [ (int(ts), name) for ts, name in csv.reader(f.readlines())]
    return events
events = getEvent()

# %% plot fun
def plot(attrib: str):
    x = [ d['rxts'] for d in data ]
    # plt.plot( [ d[attrib] for d in data ], x )
    plt.show()
    # print([ d[attrib] for d in data ])
    for i, pId in enumerate(pIds):
        y = [ d[attrib] if d['processorId'] == pId else None for d in data ]
        plt.plot(x, y, label=f'Worker {i+1} - Id:{pId}')
    # add labels
    plt.xlabel('tuple')
    plt.ylabel('latency [ms]')
    plt.legend()
    plt.show()

plot('latency')

# %%
