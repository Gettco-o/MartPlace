from abc import ABC, abstractmethod

class IdempotencyRepository(ABC):
      
      @abstractmethod
      def get(self, key: str, operation: str):
            pass

      @abstractmethod
      def save(self, record):
            pass
