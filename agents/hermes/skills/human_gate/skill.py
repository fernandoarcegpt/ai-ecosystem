#!/usr/bin/env python3
"""Human Gate implementation for Hermes Agent Ecosystem.
Manages human review requests and approvals for critical policy evaluations.
"""

import os
import sys
import json
import logging
import tempfile
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class HumanReviewRequest:
    """DTO for human review requests"""
    review_id: str
    task_description: str
    requested_by: str
    status: str = "pending"
    reason: Optional[str] = None
    reminder_sent: bool = False
    timestamp: datetime = field(default_factory=datetime.now)
    task_id: Optional[str] = None
    policy_id: Optional[str] = None  # Added for integration
    policy_reason: Optional[str] = None  # Added for integration

# Valid fields for HumanReviewRequest dataclass
VALID_HR_FIELDS = {
    "review_id", "task_description", "requested_by", "status", 
    "reason", "reminder_sent", "timestamp", "task_id", 
    "policy_id", "policy_reason"
}

class HumanGate:
    """Human Gate for managing human approvals in policy evaluation.
    
    This class handles the workflow for human-in-the-loop decision making,
    including submitting review requests and processing human decisions.
    """

    def __init__(self, storage_path: Optional[str] = None):
        """Initialize the review ledger and restore previous decisions."""
        selected = storage_path or os.getenv("HERMES_HUMAN_GATE_FILE")
        self.storage_path = Path(selected).expanduser() if selected else None
        self.review_requests: List[HumanReviewRequest] = []
        self._load()
        logger.info("Human Gate initialized")

    @staticmethod
    def _serialize(review: HumanReviewRequest) -> Dict[str, Any]:
        data = {field_name: getattr(review, field_name) for field_name in VALID_HR_FIELDS}
        data["timestamp"] = review.timestamp.isoformat()
        return data

    @staticmethod
    def _deserialize(data: Dict[str, Any]) -> HumanReviewRequest:
        item = {key: value for key, value in data.items() if key in VALID_HR_FIELDS}
        timestamp = item.get("timestamp")
        if isinstance(timestamp, str):
            item["timestamp"] = datetime.fromisoformat(timestamp)
        return HumanReviewRequest(**item)

    def _load(self) -> None:
        if self.storage_path is None or not self.storage_path.exists():
            return
        try:
            with self.storage_path.open("r", encoding="utf-8") as handle:
                payload = json.load(handle)
            self.review_requests = [self._deserialize(item) for item in payload.get("reviews", [])]
        except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
            logger.error("Could not load human review ledger: %s", exc)

    def _save(self) -> None:
        if self.storage_path is None:
            return
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        fd, temp_name = tempfile.mkstemp(prefix="human-gate-", suffix=".tmp", dir=str(self.storage_path.parent), text=True)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump({"version": 1, "reviews": [self._serialize(review) for review in self.review_requests]}, handle, indent=2, ensure_ascii=False)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temp_name, self.storage_path)
        except Exception:
            Path(temp_name).unlink(missing_ok=True)
            raise

    def submit_for_review(self,
                        task_description: str,
                        actor: str = "orchestrator",
                        metadata: Optional[Dict[str, Any]] = None) -> HumanReviewRequest:
        """Submit a task for human review.
        
        Args:
            task_description: Original task description that triggered review
            actor: Who requested the task (default: "orchestrator")
            metadata: Additional context or policy evaluation details
            
        Returns:
            HumanReviewRequest object with assigned review ID
        """
        review_id = "review-" + uuid.uuid4().hex
        # Prepare metadata
        task_metadata = {**metadata} if metadata else {}
        if task_description:
            # Use first word as task_id or generate UUID if empty
            task_id = task_description.split()[0] if task_description else "uid-" + datetime.now().strftime('%Y%m%d%H%M%S')
            task_metadata = task_metadata.copy()
            task_metadata.setdefault("task_id", task_id)
        
        # Filter metadata to only include valid HumanReviewRequest fields
        filtered_metadata = {k: v for k, v in task_metadata.items() if k in VALID_HR_FIELDS}
        
        # Create and store the review request
        review = HumanReviewRequest(
            review_id=review_id,
            task_description=task_description,
            requested_by=actor,
            **filtered_metadata
        )
        self.review_requests.append(review)
        self._save()
        logger.info(f"Submitted review request: {review_id}")
        return review

    def check_pending_reviews(self) -> List[HumanReviewRequest]:
        """Get all pending review requests
        
        Returns:
            List of pending review requests that need human action
        """
        return [r for r in self.review_requests if r.status == "pending"]

    def process_review(self,
                     review_id: str,
                     action: str,
                     additional_notes: str = "") -> bool:
        """Process a human review result
        
        Args:
            review_id: ID of the review to process
            action: Decision to make ("approve" or "reject")
            additional_notes: Optional notes from the reviewer
            
        Returns:
            True if processing succeeded, False otherwise
        """
        for review in self.review_requests:
            if review.review_id == review_id:
                if action.lower() == "approve":
                    review.status = "approved"
                    if additional_notes:
                        review.reason = f"Approved for execution: {additional_notes}"
                    else:
                        review.reason = "Approved"
                elif action.lower() == "reject":
                    review.status = "rejected"
                    if additional_notes:
                        review.reason = f"Rejected: {additional_notes}"
                    else:
                        review.reason = "Rejected"
                else:
                    logger.error(f"Invalid action: {action}")
                    return False
                
                logger.info(f"Processed review {review_id}: {action}")
                self._save()
                return True
        
        logger.error(f"Review not found: {review_id}")
        return False

    def get_review_by_id(self, review_id: str) -> Optional[HumanReviewRequest]:
        """Retrieve a review request by ID (for status checks)
        
        Args:
            review_id: ID of the review to retrieve
            
        Returns:
            HumanReviewRequest object if found, None otherwise
        """
        for r in self.review_requests:
            if r.review_id == review_id:
                return r
        return None

    def get_review_stats(self) -> Dict[str, Any]:
        """Get overall review statistics
        
        Returns:
            Dictionary with counts of pending, approved, and rejected reviews
        """
        pending = len(self.check_pending_reviews())
        completed = len([r for r in self.review_requests if r.status in ["approved", "rejected"]])
        return {"pending": pending, "completed": completed, "total": len(self.review_requests)}
