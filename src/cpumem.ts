import * as os from 'os'
import fs from 'fs'

class SysMetrics {
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
  private startBenchmarking(path: string, interval: number) {
      this.timesBefore = os.cpus().map(c => c.times);
      this.benchmarkingInterval = setInterval(() => {
          const cpuUsage = this.getCpuUsage();
          const memUsage = os.totalmem()
          const currentTimeStamp = new Date().getTime()
          const data = [currentTimeStamp, memUsage, ...cpuUsage]
          fs.appendFileSync(path, data.join(",") + '\n')
      }, interval)
  }
  private stopBenchmarking() {
      if (this.benchmarkingInterval) clearInterval(this.benchmarkingInterval)
  }

  constructor(path: string, interval: number) {
    this.startBenchmarking(path, interval)
  }
}

new SysMetrics('test.csv', 100);