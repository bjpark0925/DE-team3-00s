import asyncio
import aiohttp
import time

REQUEST_COUNT = 10000
BASE_URL = "your-url"
payload = {
    "taxi_id": 123,
    "lon": -73.9589,
    "lat": 40.7923,
}
headers = {
    "Content-Type": "application/json"
}


# 각 요청에 대한 비동기 함수
async def fetch(session, url, data):
    try:
        async with session.post(url, json=data) as response:
            if response.status == 200:
                return "Success"
            else:
                return f"Failed: {response.status}"
    except aiohttp.ClientError as e:
        return f"Error: {e}"


# 모든 요청을 관리하고 실행하는 메인 비동기 함수
async def main():
    start_time = time.time()

    # aiohttp.ClientSession을 한 번만 생성하여 여러 요청에 재사용하는 것이 효율적입니다.
    # 이는 TCP 연결 재사용을 가능하게 하여 성능을 크게 향상시킵니다.
    async with aiohttp.ClientSession() as session:
        # 10,000개의 요청에 대한 데이터와 task를 생성
        tasks = []
        for i in range(REQUEST_COUNT):
            # fetch 코루틴을 task로 만들어서 tasks 리스트에 추가
            task = asyncio.create_task(fetch(session, BASE_URL, payload))
            tasks.append(task)

        # asyncio.gather를 사용하여 모든 task를 동시에 실행하고, 모든 결과가 반환될 때까지 기다립니다.
        results = await asyncio.gather(*tasks)

    end_time = time.time()

    # 결과 분석
    success_count = results.count("Success")
    print(f"총 요청 수: {len(results)}")
    print(f"성공 요청 수: {success_count}")
    print(f"실패 요청 수: {len(results) - success_count}")
    print(f"총 소요 시간: {end_time - start_time:.2f} 초")
    print(f"초당 처리량: {REQUEST_COUNT / (end_time - start_time):.2f} req/s")


if __name__ == "__main__":
    asyncio.run(main())