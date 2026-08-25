"""First-run seeding: admin account, site settings, service images, event packages.

Every helper is idempotent — existing documents are never overwritten, so admin
edits survive a restart.
"""

from . import db, security
from .config import settings

HERO_STAGE = "/images/hero-stage.jpg"
WALK_AROUND = "/images/walk-around.jpg"
MENTALISM = "/images/mentalism.jpg"
EMCEE = "/images/emcee.jpg"

SERVICE_IMAGES = [
    {
        "slug": "stage-magic",
        "label": "01 • Stage Magic",
        "title": "Stage Magic",
        "imageUrl": HERO_STAGE,
    },
    {
        "slug": "walk-around-magic",
        "label": "02 • Walk-Around Magic",
        "title": "Walk-Around Magic",
        "imageUrl": WALK_AROUND,
    },
    {
        "slug": "mentalism",
        "label": "03 • Mentalism",
        "title": "Mentalism",
        "imageUrl": MENTALISM,
    },
    {
        "slug": "emcee",
        "label": "04 • Emcee & Interactive Entertainment",
        "title": "Emcee & Interactive Entertainment",
        "imageUrl": EMCEE,
    },
]

EVENT_PACKAGES = [
    {
        "title": "Magic + Emcee",
        "shortDescription": "One professional, the full entertainment arc of your event.",
        "fullDescription": (
            "Start with walk-around magic, move into games and audience engagement, host the "
            "event and finish with stage magic or mentalism. One booking, one coordination "
            "point, one seamless flow."
        ),
        "highlights": [
            "Complete event flow",
            "Single coordination point",
            "Cost efficient",
            "Custom run-of-show",
            "Stage + floor",
            "Full-length events",
        ],
        "imageUrl": HERO_STAGE,
        "ctaLabel": "Book The Combination",
        "ctaLink": "/book",
    },
    {
        "title": "Corporate Entertainment",
        "shortDescription": "Annual days, award nights, conferences and dealer meets.",
        "fullDescription": (
            "Entertainment built for a corporate run-of-show: clean content, brand-safe humour, "
            "tight timing and segments that can carry a product or award reveal."
        ),
        "highlights": [
            "Annual days",
            "Award nights",
            "Conferences",
            "Dealer meets",
            "Brand reveals",
            "Employee engagement",
        ],
        "imageUrl": EMCEE,
        "ctaLabel": "Enquire For Corporate",
        "ctaLink": "/book",
    },
    {
        "title": "Birthday Entertainment",
        "shortDescription": "Magic, games and hosting for a birthday people remember.",
        "fullDescription": (
            "Age-appropriate magic, participation games and hosting for children's parties, "
            "milestone birthdays and family celebrations at homes, clubhouses and party halls."
        ),
        "highlights": [
            "Kids & family shows",
            "Milestone birthdays",
            "Participation games",
            "Party hall or home",
            "Photo moments",
            "Flexible duration",
        ],
        "imageUrl": WALK_AROUND,
        "ctaLabel": "Book For A Birthday",
        "ctaLink": "/book",
    },
    {
        "title": "Wedding Entertainment",
        "shortDescription": "Guest entertainment between ceremonies, meals and celebrations.",
        "fullDescription": (
            "Weddings have waiting time. Walk-around magic and interactive moments keep guests "
            "engaged during receptions, cocktail hours and gaps in the schedule."
        ),
        "highlights": [
            "Reception entertainment",
            "Cocktail hour magic",
            "Family interaction",
            "Sangeet & mehendi",
            "Photo-friendly moments",
            "Discreet & elegant",
        ],
        "imageUrl": MENTALISM,
        "ctaLabel": "Enquire For Weddings",
        "ctaLink": "/book",
    },
    {
        "title": "Hotel / Brunch Entertainment",
        "shortDescription": "Sunday brunch and lounge experiences for luxury venues.",
        "fullDescription": (
            "A recurring guest experience for star hotels: close-up magic moving through the "
            "restaurant, giving guests a reason to stay longer and return."
        ),
        "highlights": [
            "Sunday brunches",
            "Lounge & bar",
            "Guest experience",
            "Repeat engagements",
            "Family friendly",
            "Elegant close-up",
        ],
        "imageUrl": WALK_AROUND,
        "ctaLabel": "Enquire For Hotels",
        "ctaLink": "/book",
    },
    {
        "title": "Clubhouse Entertainment",
        "shortDescription": "All-age entertainment for community and residential events.",
        "fullDescription": (
            "Community events have the toughest audience mix — children, parents and seniors "
            "together. This format is designed to bring all of them into the same experience."
        ),
        "highlights": [
            "Festival events",
            "Community days",
            "All-age content",
            "Games & hosting",
            "Outdoor or indoor",
            "Large families",
        ],
        "imageUrl": EMCEE,
        "ctaLabel": "Enquire For Clubhouse",
        "ctaLink": "/book",
    },
]

DEFAULT_SETTINGS = {
    "artistName": "Maverick Manju",
    "tagline": "Magician | Emcee | Mentalist | Creator Coach",
    "phone": "+91 98860 00000",
    "whatsapp": "919886000000",
    "email": "bookings@maverickmanju.in",
    "instagram": "https://instagram.com/maverickmanju",
    "facebook": "https://facebook.com/maverickmanju",
    "youtube": "https://youtube.com/@maverickmanju",
    "website": "maverickmanju.in",
    "defaultBookingMessage": (
        "Hi Maverick Manju, I would like to enquire about magic entertainment for my event."
    ),
    "footerCopyright": "© 2026 Maverick Manju. All Rights Reserved.",
    "googleReviewLink": "https://g.page/maverickmanju/review",
}


async def seed_admin() -> None:
    email = settings.admin_email.strip().lower()
    existing = await db.admin_users().find_one({"email": email})
    if existing:
        return
    await db.admin_users().insert_one(
        {
            "email": email,
            "name": settings.admin_name,
            "role": "admin",
            "passwordHash": security.hash_password(settings.admin_password),
            "createdAt": db.now(),
        }
    )


async def seed_service_images() -> None:
    for order, item in enumerate(SERVICE_IMAGES, start=1):
        # The label/title are ours to keep in sync; imageUrl belongs to the admin
        # once they have replaced it, so it is only written on insert.
        await db.service_images().update_one(
            {"slug": item["slug"]},
            {
                "$setOnInsert": {
                    "slug": item["slug"],
                    "imageUrl": item["imageUrl"],
                    "publicId": "",
                    "createdAt": db.now(),
                },
                "$set": {
                    "label": item["label"],
                    "title": item["title"],
                    "sortOrder": order,
                },
            },
            upsert=True,
        )


async def seed_packages() -> None:
    if await db.packages().count_documents({}) > 0:
        return
    await db.packages().insert_many(
        [
            {
                **pkg,
                "publicId": "",
                "status": "published",
                "sortOrder": order,
                "createdAt": db.now(),
                "updatedAt": db.now(),
            }
            for order, pkg in enumerate(EVENT_PACKAGES, start=1)
        ]
    )


async def seed_settings() -> None:
    await db.site_settings().update_one(
        {"_id": "site"},
        {"$setOnInsert": {**DEFAULT_SETTINGS, "updatedAt": db.now()}},
        upsert=True,
    )


async def run() -> None:
    await seed_admin()
    await seed_service_images()
    await seed_packages()
    await seed_settings()
