import FrontierTester, { FrontierTesterProps } from './Tester';

const props: FrontierTesterProps[] = [

  { n: 100,  numTuples: 100000, replicationFactor: 2, chainLength: 1, kill: false, rateLimitSrc: true,  maxSrcTotalQueueSizeTuples: 100,  maxTotalQueueSizeTuples: 100  },
  // { n: 101,  numTuples: 100000, replicationFactor: 2, chainLength: 1, kill: false, rateLimitSrc: false, maxSrcTotalQueueSizeTuples: 100,  maxTotalQueueSizeTuples: 100  },

  // { n: 102,  numTuples: 100000, replicationFactor: 2, chainLength: 1, kill: true,  rateLimitSrc: false, maxSrcTotalQueueSizeTuples: 100,  maxTotalQueueSizeTuples: 100  },
  // { n: 103,  numTuples: 100000, replicationFactor: 3, chainLength: 1, kill: true,  rateLimitSrc: false, maxSrcTotalQueueSizeTuples: 100,  maxTotalQueueSizeTuples: 100  },
  // { n: 104,  numTuples: 100000, replicationFactor: 2, chainLength: 2, kill: true,  rateLimitSrc: false, maxSrcTotalQueueSizeTuples: 100,  maxTotalQueueSizeTuples: 100  },

  // { n: 105,  numTuples: 100000, replicationFactor: 2, chainLength: 1, kill: true,  rateLimitSrc: true,  maxSrcTotalQueueSizeTuples: 100,  maxTotalQueueSizeTuples: 100  },
  // { n: 106,  numTuples: 100000, replicationFactor: 3, chainLength: 1, kill: true,  rateLimitSrc: true,  maxSrcTotalQueueSizeTuples: 100,  maxTotalQueueSizeTuples: 100  },
  // { n: 107,  numTuples: 100000, replicationFactor: 2, chainLength: 2, kill: true,  rateLimitSrc: true,  maxSrcTotalQueueSizeTuples: 100,  maxTotalQueueSizeTuples: 100  },
  
  // { n: 108,  numTuples: 100000, replicationFactor: 2, chainLength: 1, kill: true,  rateLimitSrc: false, maxSrcTotalQueueSizeTuples: 10,   maxTotalQueueSizeTuples: 10   },
  // { n: 109,  numTuples: 100000, replicationFactor: 3, chainLength: 1, kill: true,  rateLimitSrc: false, maxSrcTotalQueueSizeTuples: 10,   maxTotalQueueSizeTuples: 10   },
  
  // { n: 110, numTuples: 100000, replicationFactor: 2, chainLength: 1, kill: true,  rateLimitSrc: false, maxSrcTotalQueueSizeTuples: 1000, maxTotalQueueSizeTuples: 1000 },
  // { n: 111, numTuples: 100000, replicationFactor: 3, chainLength: 1, kill: true,  rateLimitSrc: false, maxSrcTotalQueueSizeTuples: 1000, maxTotalQueueSizeTuples: 1000 },
  
  // { n: 112, numTuples: 100000, replicationFactor: 2, chainLength: 1, kill: true,  rateLimitSrc: false, maxSrcTotalQueueSizeTuples: 5000, maxTotalQueueSizeTuples: 5000 },
  // { n: 113, numTuples: 100000, replicationFactor: 3, chainLength: 1, kill: true,  rateLimitSrc: false, maxSrcTotalQueueSizeTuples: 5000, maxTotalQueueSizeTuples: 5000 },

  // { n: 114,  numTuples: 100000, replicationFactor: 1, chainLength: 2, kill: false, rateLimitSrc: true,  maxSrcTotalQueueSizeTuples: 100,  maxTotalQueueSizeTuples: 100  },
  // { n: 115,  numTuples: 100000, replicationFactor: 2, chainLength: 2, kill: false, rateLimitSrc: true,  maxSrcTotalQueueSizeTuples: 100,  maxTotalQueueSizeTuples: 100  },

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
