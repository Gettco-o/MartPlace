class DomainError(Exception):
      pass

class InsufficientFundsError(DomainError):
      pass

class InvalidAmountError(DomainError):
      pass