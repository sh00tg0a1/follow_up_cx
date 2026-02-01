"""
Recurrence Service - Handle recurring events

Supports RRULE format for generating recurring event instances.
Uses dateutil.rrule for parsing and generating recurrence patterns.
"""
from datetime import datetime, timedelta
from typing import List, Optional, Tuple
from dateutil.rrule import rrulestr, rrule, DAILY, WEEKLY, MONTHLY, YEARLY
from dateutil.parser import parse as parse_date

from logging_config import get_logger

logger = get_logger(__name__)


def parse_recurrence_rule(rule_str: str) -> Optional[rrule]:
    """
    Parse RRULE string into rrule object
    
    Args:
        rule_str: RRULE string, e.g., "FREQ=DAILY;INTERVAL=1" or "FREQ=WEEKLY;BYDAY=MO,WE,FR"
    
    Returns:
        rrule object or None if parsing fails
    """
    try:
        # Ensure DTSTART is included if not present
        if "DTSTART" not in rule_str.upper():
            # Use current date as default DTSTART
            dtstart = datetime.now()
            rule_str = f"DTSTART:{dtstart.strftime('%Y%m%dT%H%M%S')};{rule_str}"
        
        # Parse RRULE
        rule = rrulestr(rule_str)
        return rule
    except Exception as e:
        logger.error(f"Failed to parse recurrence rule '{rule_str}': {e}")
        return None


def generate_recurrence_instances(
    start_time: datetime,
    recurrence_rule: str,
    recurrence_end: Optional[datetime] = None,
    max_instances: int = 100,
) -> List[datetime]:
    """
    Generate recurring event instances based on RRULE
    
    Args:
        start_time: Start time of the first event
        recurrence_rule: RRULE string
        recurrence_end: Optional end date/time for recurrence
        max_instances: Maximum number of instances to generate
    
    Returns:
        List of datetime instances
    """
    try:
        # Build RRULE string with DTSTART
        dtstart_str = start_time.strftime("%Y%m%dT%H%M%S")
        full_rule = f"DTSTART:{dtstart_str};{recurrence_rule}"
        
        # Parse rule
        rule = rrulestr(full_rule)
        
        # Generate instances
        instances = []
        if recurrence_end:
            # Generate until recurrence_end
            for dt in rule:
                if dt > recurrence_end:
                    break
                instances.append(dt)
                if len(instances) >= max_instances:
                    break
        else:
            # Generate up to max_instances
            for dt in rule:
                instances.append(dt)
                if len(instances) >= max_instances:
                    break
        
        logger.info(f"Generated {len(instances)} recurrence instances from rule '{recurrence_rule}'")
        return instances
    
    except Exception as e:
        logger.error(f"Failed to generate recurrence instances: {e}")
        return []


def create_simple_recurrence_rule(
    freq: str,
    interval: int = 1,
    byday: Optional[List[str]] = None,
    count: Optional[int] = None,
    until: Optional[datetime] = None,
) -> str:
    """
    Create a simple RRULE string
    
    Args:
        freq: Frequency (DAILY, WEEKLY, MONTHLY, YEARLY)
        interval: Interval between occurrences (default: 1)
        byday: List of weekdays for WEEKLY (e.g., ["MO", "WE", "FR"])
        count: Number of occurrences
        until: End date/time
    
    Returns:
        RRULE string
    """
    parts = [f"FREQ={freq.upper()}"]
    
    if interval > 1:
        parts.append(f"INTERVAL={interval}")
    
    if byday:
        parts.append(f"BYDAY={','.join(byday)}")
    
    if count:
        parts.append(f"COUNT={count}")
    
    if until:
        parts.append(f"UNTIL={until.strftime('%Y%m%dT%H%M%S')}")
    
    return ";".join(parts)


def detect_similar_events(
    title1: str,
    title2: str,
    time1: datetime,
    time2: datetime,
    similarity_threshold: float = 0.8,
    time_window_hours: int = 24,
) -> bool:
    """
    Detect if two events are similar (for merging)
    
    Args:
        title1: First event title
        title2: Second event title
        time1: First event start time
        time2: Second event start time
        similarity_threshold: Title similarity threshold (0-1)
        time_window_hours: Time window in hours for considering events as similar
    
    Returns:
        True if events are similar enough to merge
    """
    # Calculate title similarity (simple word-based)
    title1_words = set(title1.lower().split())
    title2_words = set(title2.lower().split())
    
    if not title1_words or not title2_words:
        return False
    
    # Jaccard similarity
    intersection = len(title1_words & title2_words)
    union = len(title1_words | title2_words)
    similarity = intersection / union if union > 0 else 0.0
    
    # Check time window
    time_diff = abs((time1 - time2).total_seconds() / 3600)
    within_window = time_diff <= time_window_hours
    
    # Both conditions must be met
    is_similar = similarity >= similarity_threshold and within_window
    
    logger.debug(
        f"Similarity check: '{title1}' vs '{title2}' - "
        f"similarity={similarity:.2f}, time_diff={time_diff:.1f}h, "
        f"within_window={within_window}, is_similar={is_similar}"
    )
    
    return is_similar
