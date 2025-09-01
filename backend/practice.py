import asyncio

# 코루틴 함수 정의
async def my_task(name: str, delay: int):
    print(f"[{name}] 시작")
    await asyncio.sleep(delay)   # 🛑 여기서 멈춤
    print(f"[{name}] 다시 실행 (delay={delay})")
    return f"{name} 완료!"

async def main():
    # 코루틴 두 개를 동시에 실행
    task1 = asyncio.create_task(my_task("작업 A", 3))
    task2 = asyncio.create_task(my_task("작업 B", 1))

    print("현재 루프의 Task들:", asyncio.all_tasks())

    # 두 작업 결과 기다림
    result1 = await task1
    result2 = await task2

    print("모든 작업 완료:", result1, result2)

# 이벤트 루프 실행
asyncio.run(main())