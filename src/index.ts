import path from 'path'
import { spawn, ChildProcess } from 'child_process'
import cliProgress from 'cli-progress'
import * as dotenv from 'dotenv'
import fs from 'fs'
import chalk from 'chalk'
dotenv.config()
type FrontierTesterProps = {
    replicationFactor: number
    chainLength: number
    numTuples: number
    warmUpTuples: number
    nWorkers?: number
    queryType: string
}
class FrontierTester {
    private readonly FRONTIER_PATH = "/home/toscan/dev/bd/frontier"
    private readonly EXAMPLE_PATH = path.join(this.FRONTIER_PATH, "seep-system/examples/acita_demo_2015")
    private readonly SEEP_JAR = path.join(this.EXAMPLE_PATH, "lib/seep-system-0.0.1-SNAPSHOT.jar")
    private readonly QUERY_JAR = path.join(this.EXAMPLE_PATH, "dist/acita_demo_2015.jar")
    private readonly LOG_DIR = "./logs"
    private readonly RESULTS_DIR = "./results"
    
    private readonly N_WORKERS
    private readonly N_TUPLES
    private readonly KILL_EACH
    
    private itsKillingTime = false
    private master: ChildProcess | null = null
    private workers: ChildProcess[] = []
    private sinkData: string[] = []
    private readonly props: { [key: string]: string | number }




    constructor(props: FrontierTesterProps) {
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

    public async run() {
        this.master = this.startMaster()
        await this.sleep(3)
        for (let i = 0; i < this.N_WORKERS + 2; i++) {
            const port = 3501 + i
            this.workers.push( this.startWorker(port) )
            console.log(`Started worker on port ${port}`)
            await this.sleep(0.01)
        }
        await this.sleep(2)

        console.log("Deploying query ... ")
        this.deployQuery()
        // this.progressBar.start(this.N_TUPLES, 0);
    }

    private done() {
        this.master?.kill()
        this.workers.forEach(w => w.kill())
        const sinkDataPath = path.join(this.RESULTS_DIR, `sink.csv`)
        fs.writeFileSync(sinkDataPath, this.sinkData.join("\n"))
        console.log("Done")
    }

    private sleep(s: number) {
        return new Promise(resolve => setTimeout(resolve, s * 1000))
    }

    private parseProps() {
        return Object.keys(this.props).map(k => `-D${k}=${this.props[k]}`).join(" ");
    }


    private startMaster() {
        const cmd = `java ${ this.parseProps() } -classpath "./lib/*" uk.ac.imperial.lsds.seep.Main Master \`pwd\`/dist/acita_demo_2015.jar Base`
        console.log( chalk.green( cmd ))
        const p = spawn (cmd, { 
            cwd: this.EXAMPLE_PATH,
            shell: true,
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
            shell: true
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
                this.printColored(line, port)
                // return
                const data = line.split(",")
                if (this.itsKillingTime && data[1] === "PROCESSOR") {
                    p.kill()
                    console.log("Killed worker")
                    console.log(line)
                    this.itsKillingTime = false
                } else if (data[1] === "SINK") {
                    this.progressBar.increment()
                    this.sinkData.push(line)
                    const n = +data[2]
                    if (n % this.KILL_EACH === 0) {
                        console.log(line)
                        this.itsKillingTime = true
                    } else if (n >= this.N_TUPLES) {
                        this.progressBar.stop()
                        this.done()
                    }
                }

            }
        }
    }
}

const tester = new FrontierTester({
    queryType: "join",
    // nWorkers: 20,
    replicationFactor: 2,
    chainLength: 5,
    numTuples: 15,
    warmUpTuples: 0,
})
tester.run()