#!/usr/bin/env python3
"""Human Gate implementation for Hermes Agent Ecosystem.
Manages human review requests and approvals for critical policy evaluations.
"""

import os
import sys
import json
import logging
from datetime import datetime
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

    def __init__(self):
        """Initialize with storage for review requests (simulated in-memory for now)"""
        self.review_requests = []  # In production, this would be a persistent store
        logger.info("Human Gate initialized")

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
        review_id = "review-" + datetime.now().strftime('%Y%m%d-%H%M%S')
        # Prepare metadata
        task_metadata = {**metadata} if metadata else {}
        if task_description:
            # Use first word as task_id or generate UUID if empty
            task_id = task_description.split()[0] if task_description else "uid-" + datetime.now().strftime('%Y%m%d%H%M%S')
            task_metadata = task_metadata.copy()
            task_metadata["task_id"] = task_id
        
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
                self.review_requests = [r for r in self.review_requests if r.review_id != review_id]
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