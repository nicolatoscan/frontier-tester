import FrontierTester, { FrontierTesterProps } from './Tester';

const props: FrontierTesterProps[] = [

  { numTuples: 20000, replicationFactor: 2, chainLength: 1, kill: false, rateLimitSrc: true,  maxSrcTotalQueueSizeTuples: 100,  maxTotalQueueSizeTuples: 100  },
  { numTuples: 20000, replicationFactor: 2, chainLength: 1, kill: false, rateLimitSrc: false, maxSrcTotalQueueSizeTuples: 100,  maxTotalQueueSizeTuples: 100  },

  { numTuples: 20000, replicationFactor: 2, chainLength: 1, kill: true,  rateLimitSrc: false, maxSrcTotalQueueSizeTuples: 100,  maxTotalQueueSizeTuples: 100  },
  { numTuples: 20000, replicationFactor: 3, chainLength: 1, kill: true,  rateLimitSrc: false, maxSrcTotalQueueSizeTuples: 100,  maxTotalQueueSizeTuples: 100  },
  { numTuples: 20000, replicationFactor: 2, chainLength: 2, kill: true,  rateLimitSrc: false, maxSrcTotalQueueSizeTuples: 100,  maxTotalQueueSizeTuples: 100  },

  { numTuples: 20000, replicationFactor: 2, chainLength: 1, kill: true,  rateLimitSrc: true,  maxSrcTotalQueueSizeTuples: 100,  maxTotalQueueSizeTuples: 100  },
  { numTuples: 20000, replicationFactor: 3, chainLength: 1, kill: true,  rateLimitSrc: true,  maxSrcTotalQueueSizeTuples: 100,  maxTotalQueueSizeTuples: 100  },
  { numTuples: 20000, replicationFactor: 2, chainLength: 2, kill: true,  rateLimitSrc: true,  maxSrcTotalQueueSizeTuples: 100,  maxTotalQueueSizeTuples: 100  },
  
  { numTuples: 20000, replicationFactor: 2, chainLength: 1, kill: true,  rateLimitSrc: false, maxSrcTotalQueueSizeTuples: 10,   maxTotalQueueSizeTuples: 10   },
  { numTuples: 20000, replicationFactor: 3, chainLength: 1, kill: true,  rateLimitSrc: false, maxSrcTotalQueueSizeTuples: 10,   maxTotalQueueSizeTuples: 10   },
  
  { numTuples: 20000, replicationFactor: 2, chainLength: 1, kill: true,  rateLimitSrc: false, maxSrcTotalQueueSizeTuples: 1000, maxTotalQueueSizeTuples: 1000 },
  { numTuples: 20000, replicationFactor: 3, chainLength: 1, kill: true,  rateLimitSrc: false, maxSrcTotalQueueSizeTuples: 1000, maxTotalQueueSizeTuples: 1000 },
  
  { numTuples: 20000, replicationFactor: 2, chainLength: 1, kill: true,  rateLimitSrc: false, maxSrcTotalQueueSizeTuples: 5000, maxTotalQueueSizeTuples: 5000 },
  { numTuples: 20000, replicationFactor: 3, chainLength: 1, kill: true,  rateLimitSrc: false, maxSrcTotalQueueSizeTuples: 5000, maxTotalQueueSizeTuples: 5000 },

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