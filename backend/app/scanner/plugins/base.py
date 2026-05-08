from abc import ABC, abstractmethod
from typing import List, Dict, Any
import httpx

class BaseDetector(ABC):
    def __init__(self, client: httpx.AsyncClient):
        self.client = client

    @abstractmethod
    async def detect(self, url: str, html: str) -> List[Dict[str, Any]]:
        pass
