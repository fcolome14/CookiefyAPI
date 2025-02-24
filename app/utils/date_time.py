from abc import ABC, abstractmethod
from datetime import datetime, timedelta, timezone
from app.core.config import settings

# Strategy Pattern
class DateFormatter(ABC):
    """Abstract base class for date formatting strategies."""
    @abstractmethod
    def format(self, date: datetime) -> str:
        pass

class ISODateFormatter(DateFormatter):
    """Concrete strategy for ISO8601 formatting."""
    def format(self, date: datetime) -> str:
        return date.isoformat()

class USDateFormatter(DateFormatter):
    """Concrete strategy for US formatting."""
    def format(self, date: datetime) -> str:
        return date.strftime("%m/%d/%Y")

class EUDateFormatter(DateFormatter):
    """Concrete strategy for EU formatting."""
    def format(self, date: datetime) -> str:
        return date.strftime("%d/%m/%Y")

# Factory Pattern
class DateFactory:
    """Factory for creating date objects."""
    @staticmethod
    def now() -> datetime:
        return datetime.now()

    @staticmethod
    def from_string(date_str: str, fmt: str = "%Y-%m-%d") -> datetime:
        return datetime.strptime(date_str, fmt)

# Singleton Pattern
class DateUtils:
    """Singleton for managing date utilities."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DateUtils, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self.formatter: DateFormatter = ISODateFormatter()

    def set_formatter(self, formatter: DateFormatter):
        """Set the desired date formatting strategy."""
        self.formatter = formatter

    def format_date(self, date: datetime) -> str:
        """Format a date using the current strategy."""
        return self.formatter.format(date)

    def days_between(self, start: datetime, end: datetime) -> int:
        """Calculate the number of days between two dates."""
        return (end - start).days

    def add_days(self, date: datetime, days: int) -> datetime:
        """Add days to a date."""
        return date + timedelta(days=days)
    
class TimeUtils:
    """Singleton for managing time utilities."""
    
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TimeUtils, cls).__new__(cls)
        return cls._instance

    @staticmethod
    def exp_time() -> datetime:
        """Generate expiration time for auth code."""
        exp_date = datetime.now(timezone.utc) + timedelta(
            minutes=settings.email_code_expire_minutes
        )
        return exp_date