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
    
    from datetime import datetime, timezone

    def is_times_exp(self, exp_timestamp) -> dict:
        """Check if a timestamp has expired, supporting both int (Unix) and datetime."""
        
        if isinstance(exp_timestamp, int):
            try:
                expiration_date = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
            except (OSError, ValueError):
                return {"status": "error", "message": "Invalid Unix timestamp provided."}
        elif isinstance(exp_timestamp, datetime):
            expiration_date = exp_timestamp.astimezone(timezone.utc)
        else:
            return {"status": "error", "message": "The 'exp_timestamp' must be a valid integer (Unix timestamp) or datetime object."}
        
        has_expired = datetime.now(timezone.utc) > expiration_date
        return {"status": "success", "message": has_expired, "expiration_date": expiration_date.isoformat()}


    @staticmethod
    def exp_time(_time: int = settings.access_token_expire_minutes) -> datetime:
        """Generate expiration time for auth code."""
        exp_date = datetime.now(timezone.utc) + timedelta(
            minutes=_time
        )
        return exp_date