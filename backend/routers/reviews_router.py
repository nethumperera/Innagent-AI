# ════════════════════════════════════════════════════════════════
# InnAgent AI — Reviews Router
# GET/POST review drafts
# ════════════════════════════════════════════════════════════════

from fastapi import APIRouter, HTTPException
from typing import Optional
from backend.models import ReviewApproval
from backend.database import (
    get_reviews_by_hotel, update_review, save_review,
)
from backend.utils.logger import get_logger

router = APIRouter(prefix="/reviews", tags=["Reviews"])
logger = get_logger("reviews_router")


@router.get("/{hotel_id}")
async def list_reviews(hotel_id: str, status: Optional[str] = None):
    """Get all reviews for a hotel, optionally filtered by status."""
    try:
        reviews = get_reviews_by_hotel(hotel_id, status=status)
        return {"hotel_id": hotel_id, "reviews": reviews, "count": len(reviews)}
    except Exception as e:
        logger.error(f"Failed to list reviews: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/action")
async def review_action(action: ReviewApproval):
    """Approve, reject, or edit a review response draft."""
    try:
        update_data = {}

        if action.action == "approve":
            update_data["response_status"] = "approved"
            update_data["approved_by"] = action.approved_by
            logger.info(f"Review {action.review_id} approved by {action.approved_by}")

        elif action.action == "reject":
            update_data["response_status"] = "skipped"
            logger.info(f"Review {action.review_id} rejected")

        elif action.action == "edit":
            if not action.edited_response:
                raise HTTPException(status_code=400, detail="edited_response required for edit action")
            update_data["response_draft"] = action.edited_response
            update_data["response_status"] = "draft_ready"
            logger.info(f"Review {action.review_id} edited")

        result = update_review(action.review_id, update_data)
        if not result:
            raise HTTPException(status_code=404, detail="Review not found")

        return {"message": f"Review {action.action}d successfully", "review": result}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Review action failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/add")
async def add_review(
    hotel_id: str,
    platform: str,
    reviewer_name: str,
    star_rating: int,
    review_text: str,
):
    """Manually add a review for processing."""
    try:
        review_data = {
            "hotel_id": hotel_id,
            "platform": platform,
            "reviewer_name": reviewer_name,
            "star_rating": star_rating,
            "review_text": review_text,
            "response_status": "pending",
        }
        result = save_review(review_data)
        logger.info(f"Review added for hotel {hotel_id} from {platform}")
        return result
    except Exception as e:
        logger.error(f"Failed to add review: {e}")
        raise HTTPException(status_code=500, detail=str(e))
