import asyncio

async def fn(x):
    for _ in range(10000):
        print(str(x))

tasks = [ fn(x) for x in range(10) ]

async def main():
    await asyncio.gather(*tasks)

asyncio.run(main())
