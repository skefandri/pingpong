import asyncio

async def my_coroutine():
    print("Hello")
    await asyncio.sleep(10)  # Pauses here for 1 second
    print("World")

asyncio.run(my_coroutine())