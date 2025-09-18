import asyncio

# 异步 return 函数示例
async def async_add(a, b):
    """异步返回两个数的和"""
    await asyncio.sleep(1)  # 模拟异步操作
    return a + b

async def async_main():
    result = await async_add(3, 5)
    print(f"异步 return 函数返回值: {result}")

# 异步 yield 函数示例
async def async_countdown(n):
    """异步生成从 n 到 1 的倒计时"""
    while n > 0:
        await asyncio.sleep(1)  # 模拟异步操作
        yield n
        n -= 1

# 使用 for 循环和 await anext 获取异步 yield 返回值
async def async_yield_main():
    countdown_gen = async_countdown(3)
    print("使用 await anext 获取异步 yield 返回值:")
    try:
        while True:
            number = await anext(countdown_gen)
            print(number)
    except StopAsyncIteration:
        pass

    print("使用 for 循环获取异步 yield 返回值:")
    async for number in async_countdown(3):
        print(number)

# 运行异步主函数
asyncio.run(async_main())
asyncio.run(async_yield_main())
