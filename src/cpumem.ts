import fs from 'fs'
import pidusage from 'pidusage';

export default class CpuMem {

    private readonly MONITORING_FILE

    constructor(filename: string, pids: number[]) {
        this.MONITORING_FILE = filename;

        if (fs.existsSync(this.MONITORING_FILE)) {
            console.log(`File ${this.MONITORING_FILE} already exists`);
            process.exit(1);
            return;
        }

        this.sysMonitoring(pids);
    }


    private sysMonitoring(pids: number[]) {
        const compute = async () => {
            const stats = await pidusage(pids)
            const keys = Object.keys(stats);
            const firstTimestamp = stats[keys[0]]?.timestamp ?? null
            if (firstTimestamp === null) {
                return false
            }
            const line = keys.map(pid => ({ s: stats[pid], pid }))
                            .map(({ s, pid }) => `${pid},${s?.cpu ?? 0},${s?.memory ?? 0}`)
                            .join("\t")

            console.log(line);
            fs.appendFileSync(this.MONITORING_FILE, `${firstTimestamp}\t${line}\n`);
            return true
        }
        const interval = async (time: number) => {
            setTimeout(async () => {
                if (await compute())
                    interval(time);
            }, time)
        }
        interval(1000)
    }

}

if (require.main === module) {
    const filename = process.argv[2]
    const pids = process.argv.slice(3).map(x => parseInt(x))
    new CpuMem(filename, pids)
}