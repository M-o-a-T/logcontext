import anyio
import logging
from logcontext import main_context, context_of, log_tree

async def delay(x):
    with context_of("delay %.2f", x):
        await anyio.sleep(x)

async def test():
    async with anyio.create_task_group() as tg:
        with context_of("test", trace_level=logging.DEBUG):
            tg.start_soon(delay,0.1)
            tg.start_soon(delay,0.2)
            tg.start_soon(delay,0.25)
            await anyio.sleep(0.15)
            log_tree()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    with main_context():
        anyio.run(test)
