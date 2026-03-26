from abc import ABC, abstractmethod

class IdempotencyRepository(ABC):
      
      @abstractmethod
      async def get(self, key: str, operation: str):
            pass

      @abstractmethod
      async def save(self, record):
            pass
