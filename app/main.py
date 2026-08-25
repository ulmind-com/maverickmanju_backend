"""Maverick Manju API — FastAPI + MongoDB + Cloudinary."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import db, seed
from .config import settings
from .routers import auth, bookings, gallery, packages, services, settings as site, testimonials, uploads


@asynccontextmanager
async def lifespan(_: FastAPI):
    await db.create_indexes()
    await seed.run()
    yield
    await db.close()


app = FastAPI(
    title="Maverick Manju API",
    version="1.0.0",
    description="Backend for the Maverick Manju website: gallery, testimonials, services, "
    "event packages, booking enquiries and the admin panel.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_origin_regex=settings.cors_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for router in (
    auth.router,
    gallery.public,
    gallery.admin,
    testimonials.public,
    testimonials.admin,
    services.public,
    services.admin,
    packages.public,
    packages.admin,
    bookings.public,
    bookings.admin,
    site.public,
    site.admin,
    uploads.router,
):
    app.include_router(router)


@app.get("/", tags=["health"])
async def root():
    return {"service": "maverick-manju-api", "status": "ok", "docs": "/docs"}


@app.get("/api/health", tags=["health"])
async def health():
    """Confirms the process is up and Mongo is reachable."""
    await db.client().admin.command("ping")
    return {"status": "ok", "database": settings.mongodb_db}
