from fastapi import APIRouter
from .listing import router as listing_router
from .actions import router as actions_router
from .stats import router as stats_router

router = APIRouter(prefix="/evacuee", tags=["Evacuee"])

# Stats routes must be included before listing
# to prevent /summary being caught by /{id}
router.include_router(stats_router)
router.include_router(listing_router)
router.include_router(actions_router)