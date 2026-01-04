from fastapi import APIRouter

from .generate import router as generate_router
from .blogs import router as blogs_router
from .rewrite import router as rewrite_router
from .publish import router as publish_router
from .admin import router as admin_router
from .stats import router as stats_router

router = APIRouter(prefix="/api/v1")

router.include_router(generate_router)
router.include_router(blogs_router)
router.include_router(rewrite_router)
router.include_router(publish_router)
router.include_router(admin_router)
router.include_router(stats_router)
