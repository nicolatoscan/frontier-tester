import FrontierTester, { FrontierTesterProps } from './Tester';

const props: FrontierTesterProps[] = [

  { n: 0,  numTuples: 20000, replicationFactor: 2, chainLength: 1, kill: false, rateLimitSrc: true,  maxSrcTotalQueueSizeTuples: 100,  maxTotalQueueSizeTuples: 100  },
  { n: 1,  numTuples: 20000, replicationFactor: 2, chainLength: 1, kill: false, rateLimitSrc: false, maxSrcTotalQueueSizeTuples: 100,  maxTotalQueueSizeTuples: 100  },

  { n: 2,  numTuples: 20000, replicationFactor: 2, chainLength: 1, kill: true,  rateLimitSrc: false, maxSrcTotalQueueSizeTuples: 100,  maxTotalQueueSizeTuples: 100  },
  { n: 3,  numTuples: 20000, replicationFactor: 3, chainLength: 1, kill: true,  rateLimitSrc: false, maxSrcTotalQueueSizeTuples: 100,  maxTotalQueueSizeTuples: 100  },
  { n: 4,  numTuples: 20000, replicationFactor: 2, chainLength: 2, kill: true,  rateLimitSrc: false, maxSrcTotalQueueSizeTuples: 100,  maxTotalQueueSizeTuples: 100  },

  { n: 5,  numTuples: 20000, replicationFactor: 2, chainLength: 1, kill: true,  rateLimitSrc: true,  maxSrcTotalQueueSizeTuples: 100,  maxTotalQueueSizeTuples: 100  },
  { n: 6,  numTuples: 20000, replicationFactor: 3, chainLength: 1, kill: true,  rateLimitSrc: true,  maxSrcTotalQueueSizeTuples: 100,  maxTotalQueueSizeTuples: 100  },
  { n: 7,  numTuples: 20000, replicationFactor: 2, chainLength: 2, kill: true,  rateLimitSrc: true,  maxSrcTotalQueueSizeTuples: 100,  maxTotalQueueSizeTuples: 100  },
  
  { n: 8,  numTuples: 20000, replicationFactor: 2, chainLength: 1, kill: true,  rateLimitSrc: false, maxSrcTotalQueueSizeTuples: 10,   maxTotalQueueSizeTuples: 10   },
  { n: 9,  numTuples: 20000, replicationFactor: 3, chainLength: 1, kill: true,  rateLimitSrc: false, maxSrcTotalQueueSizeTuples: 10,   maxTotalQueueSizeTuples: 10   },
  
  { n: 10, numTuples: 20000, replicationFactor: 2, chainLength: 1, kill: true,  rateLimitSrc: false, maxSrcTotalQueueSizeTuples: 1000, maxTotalQueueSizeTuples: 1000 },
  { n: 11, numTuples: 20000, replicationFactor: 3, chainLength: 1, kill: true,  rateLimitSrc: false, maxSrcTotalQueueSizeTuples: 1000, maxTotalQueueSizeTuples: 1000 },
  
  { n: 12, numTuples: 20000, replicationFactor: 2, chainLength: 1, kill: true,  rateLimitSrc: false, maxSrcTotalQueueSizeTuples: 5000, maxTotalQueueSizeTuples: 5000 },
  { n: 13, numTuples: 20000, replicationFactor: 3, chainLength: 1, kill: true,  rateLimitSrc: false, maxSrcTotalQueueSizeTuples: 5000, maxTotalQueueSizeTuples: 5000 },

]

async function main() {
  for (const prop of props) {
    console.log(`Starting experiment with ${JSON.stringify(prop)}.`);
    const tester = new FrontierTester(prop);
    await tester.run();
  }
}

if (require.main === module) {
  main();
}
