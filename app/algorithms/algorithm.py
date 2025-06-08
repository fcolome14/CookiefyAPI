from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.schemas.post import ListKPIs, SiteKPIs, Score
from app.services.auth_service import AuthCodeManager
from app.utils.date_time import TimeUtils
import logging
from app.repositories.post_repo import PostRepository
from abc import ABC, abstractmethod
from app.utils.date_time import DateUtils

logger = logging.getLogger(__name__)


class IAlgorithms(ABC):
    """Interface service for managing algorithms."""

    @abstractmethod
    def compute_list_score(self) -> Score | None:
        pass
    
    @abstractmethod
    def compute_site_score(self) -> Score | None:
        pass

    @abstractmethod
    def compute_hashtag_score(self) -> Score | None:
        pass

class Score(IAlgorithms):
    """Scoring algorithm computation."""

    def __init__(self):
        pass


    def compute_list_score(self, input_metrics: ListKPIs) -> Score | None:
        """Compute list scoring value."""
        
        wc = 0.05
        wl = 1.5   
        wshs = 2.0
        wsvs = 1.75
        decay_age = 0.21
        rate_constant = 100
        penalty = 0.1

        age = max(0.01, DateUtils().days_between(
            input_metrics.created_at, 
            datetime.now(timezone.utc)
        ))


        denominator = (age + rate_constant) ** decay_age
        likes_rate  = input_metrics.likes  / denominator
        clicks_rate = input_metrics.visit_count / denominator
        shares_rate = input_metrics.shares / denominator
        saves_rate  = input_metrics.saves  / denominator

        bs = (
            wc   * clicks_rate +
            wl   * likes_rate +
            wshs * shares_rate +
            wsvs * saves_rate
        )

        penalty_factor = 1 - penalty
        score = bs * penalty_factor if input_metrics.image == 1 else bs
        score = round(score, 5)

        return max(score, 0.0)
    

    def compute_site_score(self, input_metrics: SiteKPIs) -> Score | None:
        """Compute site scoring value."""
        
        wc = 0.05
        wl = 1.5
        
        score = (wc * input_metrics.click_count + wl * input_metrics.lists_count)/100
        score = round(score, 5)

        return max(score, 0.0)


    def compute_hashtag_score(self) -> Score | None:
        pass



    