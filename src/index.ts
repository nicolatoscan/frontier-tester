import path from 'path'
import { spawn, ChildProcess } from 'child_process'
import cliProgress from 'cli-progress'
import * as dotenv from 'dotenv'
import fs, { stat } from 'fs'
import chalk from 'chalk'
import pidusage from 'pidusage';
import { parseArgs } from "node:util";

dotenv.config()

type FrontierTesterProps = {
    replicationFactor: number
    chainLength: number
    numTuples: number
    warmUpTuples: number
    nWorkers?: number
    queryType: string,
    folder: string,
    keepalive: boolean,
}
class FrontierTester {
    private readonly FRONTIER_PATH = "/home/toscan/dev/bd/frontier"
    private readonly EXAMPLE_PATH = path.join(this.FRONTIER_PATH, "seep-system/examples/acita_demo_2015")
    private readonly SEEP_JAR = path.join(this.EXAMPLE_PATH, "lib/seep-system-0.0.1-SNAPSHOT.jar")
    private readonly QUERY_JAR = path.join(this.EXAMPLE_PATH, "dist/acita_demo_2015.jar")
    private readonly LOG_DIR = "./logs"
    private readonly RESULTS_DIR = "./results"
    private readonly MONITORING_FILE
    private readonly PIDSMAP
    private readonly EVENTS_FILE
    private readonly SINK_FILE
    
    private readonly N_WORKERS
    private readonly N_TUPLES
    private readonly KILL_EACH
    
    private itsKillingTime = false
    private monitoring: ChildProcess | null = null
    private master: ChildProcess | null = null
    private workers: ChildProcess[] = []
    private sinkData: string[] = []
    private readonly props: { [key: string]: string | number }
    private starting = true;
    private pidNames: { [id: number]: string } = {}
    private readonly keepAlive: boolean

    constructor(props: FrontierTesterProps) {
        fs.mkdirSync(path.join(this.RESULTS_DIR, props.folder))
        this.MONITORING_FILE = path.join(this.RESULTS_DIR, props.folder, 'monitoring.csv')
        this.PIDSMAP = path.join(this.RESULTS_DIR, props.folder, 'pidMap.csv')
        this.EVENTS_FILE = path.join(this.RESULTS_DIR, props.folder, 'events.csv')
        this.SINK_FILE = path.join(this.RESULTS_DIR, props.folder, 'sink.csv')

        this.props = {
            "replicationFactor": props.replicationFactor,
            "chainLength": props.chainLength,
            "numTuples": props.numTuples,
            "warmUpTuples": props.warmUpTuples,
            "queryType": props.queryType,
        }
        this.N_WORKERS = props.nWorkers ?? props.replicationFactor * props.chainLength
        this.N_TUPLES = props.numTuples
        this.KILL_EACH = Math.ceil(this.N_TUPLES / (this.N_WORKERS)) + 1
        this.keepAlive = props.keepalive
    }

    private progressBar = new cliProgress.SingleBar({}, cliProgress.Presets.shades_classic)

    private printColored(text: string, port: number | null = null) {
        if (port === null) {
            console.log(chalk.red(text))
            return
        }

        const color = port % 3501
        switch (color) {
            case  0: console.log(port, chalk.green         (text) ); break
            case  1: console.log(port, chalk.blue          (text) ); break
            case  2: console.log(port, chalk.yellow        (text) ); break
            case  3: console.log(port, chalk.magenta       (text) ); break
            case  4: console.log(port, chalk.cyan          (text) ); break
            case  5: console.log(port, chalk.white         (text) ); break
            case  6: console.log(port, chalk.gray          (text) ); break
            case  7: console.log(port, chalk.black         (text) ); break
            case  8: console.log(port, chalk.redBright     (text) ); break
            case  9: console.log(port, chalk.greenBright   (text) ); break
            case 10: console.log(port, chalk.blueBright    (text) ); break
            case 11: console.log(port, chalk.yellowBright  (text) ); break
            case 12: console.log(port, chalk.magentaBright (text) ); break
            case 13: console.log(port, chalk.cyanBright    (text) ); break
            case 14: console.log(port, chalk.whiteBright   (text) ); break
            default: console.log(port, text);                        break
        }
    }

    private cleaup() {
        if (fs.existsSync(this.MONITORING_FILE))
            fs.unlinkSync(this.MONITORING_FILE)
        if (fs.existsSync(this.EVENTS_FILE))
            fs.unlinkSync(this.EVENTS_FILE)
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
            // print all cpu
            const cc = Object.keys(stats).map(pid => stats[pid]?.cpu ?? -69)

            fs.appendFileSync(this.MONITORING_FILE, `${firstTimestamp}\t${line}\n`)
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

    public async run() {
        this.cleaup()
        
        this.master = this.startMaster()
        await this.sleep(3)
        for (let i = 0; i < this.N_WORKERS + 2; i++) {
            const port = 3501 + i
            this.workers.push( this.startWorker(port) )
            console.log(`Started worker on port ${port}`)
            await this.sleep(1)
        }
        // this.monitoring = this.startMonitoring();
        await this.sleep(1)
        this.sysMonitoring(this.workers.filter(w => w.pid !== undefined).map(w => w.pid as number))
        await this.sleep(1)

        console.log("Deploying query ... ");
        this.deployQuery();
        this.progressBar.start(this.N_TUPLES, 0);
    }

    private async done() {
        await this.sleep(1);

        this.monitoring?.kill()
        this.master?.kill()
        this.workers.forEach(w => w.kill())
        fs.writeFileSync(this.SINK_FILE, this.sinkData.join("\n"))
        console.log("Done")
    }

    private sleep(s: number) {
        return new Promise(resolve => setTimeout(resolve, s * 1000))
    }

    private parseProps() {
        return Object.keys(this.props).map(k => `-D${k}=${this.props[k]}`).join(" ");
    }

    private startMaster() {
        const cmd = `${ this.parseProps() } -classpath "./lib/*" uk.ac.imperial.lsds.seep.Main Master \`pwd\`/dist/acita_demo_2015.jar Base`
        const params = cmd.split(" ")
        console.log(this.EXAMPLE_PATH)

        console.log( chalk.green( cmd ))
        const p = spawn ('java', params, { 
            cwd: this.EXAMPLE_PATH,
            shell: '/bin/zsh',
        })
        p.stdout.on('data', (data) => {
            const line = data.toString()
            this.printColored(line)
            // if (line.startsWith("PY,")) this.printColored(line)
        })
        return p
    }

    private startWorker(port: number) {
        const cmd = `java ${ this.parseProps() } -classpath "./lib/*" uk.ac.imperial.lsds.seep.Main Worker ${port}`;
        console.log( chalk.green( cmd ))
        const p = spawn (cmd, {
            cwd: this.EXAMPLE_PATH, 
            shell: '/bin/zsh',
            // detached: true,
        })
        p.stdout.on('data', (data) => {
            // this.printColored(data, port)
            this.handlesStdoutWorkers(data, p, port)
        })
        return p
    }

    private deployQuery() {
        this.master?.stdin?.write('7\n')
    }

    private handlesStdoutWorkers(data: string, p: ChildProcess, port: number) {
        for (const line of data.toString().split("\n")) {
            if (line.startsWith("PY,")) {
                if (this.starting) {
                    this.starting = false;
                    this.log('STARTED')
                } 
                // this.printColored(line, port)
                // return
                const data = line.split(",")
                this.pidNames[p.pid!] = data[1]
                if (this.itsKillingTime && data[1] === "PROCESSOR") {
                    if (!this.keepAlive) {
                        p.kill()
                        console.log("\nKilled worker\n")
                        this.log('KILLED')
                    }
                    // console.log(line)
                    this.itsKillingTime = false
                } else if (data[1] === "SINK") {
                    this.progressBar.increment()
                    this.sinkData.push(line)
                    const n = +data[2]
                    if (n % this.KILL_EACH === 0) {
                        // console.log("\nSetting killing\n")
                        this.itsKillingTime = true
                    } else if (n >= this.N_TUPLES) {
                        this.progressBar.stop()
                        this.log('DONE')
                        this.done()
                        fs.writeFileSync(this.PIDSMAP, Object.keys(this.pidNames).map(k => `${k},${this.pidNames[+k]}`).join("\n"))
                    }
                }
            }
        }
    }

    private log(name: string) {
        fs.appendFileSync(this.EVENTS_FILE, `${new Date().getTime()},${name}\n`)
    }
}

const params = parseArgs({
    options: {
        folder:         { type: "string", short: "f" },
        query:          { type: "string", short: "q", default: "chain" },
        replication:    { type: "string", short: "r", default: "3" },
        length:         { type: "string", short: "l", default: "1" },
        tuples:         { type: "string", short: "t", default: "20000" },
        warmup:         { type: "string", short: "w", default: "0" },
        keepalive:      { type: "boolean", short: "k" },
    },
});

if (!params.values.folder) {
    console.log("Please specify a folder")
    process.exit(1)
}

console.log('Args: ', params.values)

const tester = new FrontierTester({
    queryType: params.values.query!,
    // nWorkers: 20,
    replicationFactor: +params.values.replication!,
    chainLength: +params.values.length!,
    numTuples:  +params.values.tuples!,
    warmUpTuples: +params.values.warmup!,
    folder: params.values.folder!,
    keepalive: params.values.keepalive ?? false,
})
tester.run()