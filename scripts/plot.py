# %% imports
import matplotlib.pyplot as plt

# %% read result file
headers = [ "Workername","cnt","id","ts","txts","rxts","latency","bytes","latencyBreakdown","processorId"]

data = []
with open('../results/sink.csv', 'r') as f:
    for line in f:
        [ _, workername, cnt, id, ts, txts, rxts, latency, bytes, latencyBreakdown, processorId, shish ] = line.split(',')
        data.append({
            "Workername": workername,
            "cnt": int(cnt),
            "id": int(id),
            "ts": int(ts),
            "txts": int(txts),
            "rxts": int(rxts),
            "latency": int(latency),
            "bytes": int(bytes),
            "latencyBreakdown": [ int(x) for x in latencyBreakdown.split(';') ],
            "processorId": int(processorId),
        })
pIds = set( [ d['processorId'] for d in data ] )
data[0]['diff'] = 0
for i in range(1, len(data)):
    data[i]['diff'] = data[i]['rxts'] - data[i-1]['rxts']

# %% plot fun
def plot(attrib: str):
    plt.plot( [ d[attrib] for d in data ] )
    plt.show()
    # print([ d[attrib] for d in data ])
    for i, pId in enumerate(pIds):
        plt.plot([ d[attrib] if d['processorId'] == pId else None for d in data ], label=f'Worker {i+1} - Id:{pId}')
    # add labels
    plt.xlabel('tuple')
    plt.ylabel('latency [ms]')
    plt.legend()
    plt.show()

# %% plot diff
plot('latency')

# %%
