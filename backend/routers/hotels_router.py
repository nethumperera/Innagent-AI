# ════════════════════════════════════════════════════════════════
# InnAgent AI — Hotels Router
# CRUD for hotel profiles
# ════════════════════════════════════════════════════════════════

from fastapi import APIRouter, HTTPException
from backend.models import HotelCreate, HotelUpdate
from backend.database import (
    get_all_hotels, get_hotel_by_id, create_hotel,
    update_hotel, delete_hotel, get_rooms_by_hotel,
)
from backend.utils.logger import get_logger

router = APIRouter(prefix="/hotels", tags=["Hotels"])
logger = get_logger("hotels_router")


@router.get("/")
async def list_hotels(active_only: bool = True):
    """List all hotels managed by Co Host Ceylon."""
    try:
        hotels = get_all_hotels(active_only=active_only)
        return {"hotels": hotels, "count": len(hotels)}
    except Exception as e:
        logger.error(f"Failed to list hotels: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{hotel_id}")
async def get_hotel(hotel_id: str):
    """Get a specific hotel profile with rooms."""
    try:
        hotel = get_hotel_by_id(hotel_id)
        if not hotel:
            raise HTTPException(status_code=404, detail="Hotel not found")
        rooms = get_rooms_by_hotel(hotel_id)
        hotel["rooms"] = rooms
        return hotel
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get hotel {hotel_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/")
async def create_new_hotel(hotel: HotelCreate):
    """Create a new hotel profile."""
    try:
        data = hotel.model_dump(exclude_none=True)
        result = create_hotel(data)
        logger.info(f"Hotel created: {result.get('name')}")
        return result
    except Exception as e:
        logger.error(f"Failed to create hotel: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{hotel_id}")
async def update_existing_hotel(hotel_id: str, hotel: HotelUpdate):
    """Update a hotel profile."""
    try:
        data = hotel.model_dump(exclude_none=True)
        if not data:
            raise HTTPException(status_code=400, detail="No fields to update")
        result = update_hotel(hotel_id, data)
        if not result:
            raise HTTPException(status_code=404, detail="Hotel not found")
        logger.info(f"Hotel updated: {hotel_id}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update hotel {hotel_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{hotel_id}")
async def deactivate_hotel(hotel_id: str):
    """Deactivate a hotel (soft delete)."""
    try:
        delete_hotel(hotel_id)
        logger.info(f"Hotel deactivated: {hotel_id}")
        return {"message": "Hotel deactivated", "hotel_id": hotel_id}
    except Exception as e:
        logger.error(f"Failed to deactivate hotel {hotel_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
