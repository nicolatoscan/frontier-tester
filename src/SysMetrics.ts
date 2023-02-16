import * as os from 'os'
import fs from 'fs'

export default class SysMetrics {
    private path: string;
    private interval: number;

    private timesBefore = os.cpus().map(c => c.times);
    private getCpuUsage() {
        const timesAfter = os.cpus().map(c => c.times);
        const timeDeltas = timesAfter.map((t, i) => ({
            user: t.user - this.timesBefore[i].user,
            sys: t.sys - this.timesBefore[i].sys,
            idle: t.idle - this.timesBefore[i].idle
        }));
        this.timesBefore = timesAfter;
        return timeDeltas.map(times => 1 - times.idle / (times.user + times.sys + times.idle));
    }

    private benchmarkingInterval: NodeJS.Timer | null = null;
    public start() {
        this.timesBefore = os.cpus().map(c => c.times);
        this.benchmarkingInterval = setInterval(() => {
            const cpuUsage = this.getCpuUsage();
            const memUsage = os.totalmem() - os.freemem()
            const currentTimeStamp = new Date().getTime()
            const avgCpuUsage = cpuUsage.reduce((a, b) => a + b, 0) / cpuUsage.length
            const data = [currentTimeStamp, memUsage, ...cpuUsage, avgCpuUsage]
            fs.appendFileSync(this.path, data.join(",") + '\n')
        }, this.interval)
    }
    public stop() {
        if (this.benchmarkingInterval) clearInterval(this.benchmarkingInterval)
    }

    constructor(path: string, interval: number) {
        this.path = path;
        this.interval = interval;
    }
}
