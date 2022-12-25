from httpx import AsyncClient
from typing import Union, Dict, List


async def detect_http(host: str, proxies: Union[str, None], timeout: int) -> bool:
    async with AsyncClient(
        proxies=proxies, verify=False, follow_redirects=True, timeout=timeout
    ) as client:
        try:
            respond = await client.get(url=host)
        except:
            return False
        if not respond:
            return False
        if respond.status_code != 200:
            return False
        return True
