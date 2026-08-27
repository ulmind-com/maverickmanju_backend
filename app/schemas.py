"""Request/response models. Field names match the frontend TypeScript types."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

MediaType = Literal["image", "video"]
PublishStatus = Literal["published", "draft"]
GalleryLayout = Literal["small", "medium", "large", "tall", "wide"]
BookingStatus = Literal["new", "contacted", "confirmed", "completed", "cancelled"]

# The headings gallery items are grouped under on the public page, in display order.
GalleryCategory = Literal["Stage Magic", "Emcee", "Walk Around", "Mentalism"]
GALLERY_CATEGORIES = ("Stage Magic", "Emcee", "Walk Around", "Mentalism")

SERVICE_SLUGS = ("stage-magic", "walk-around-magic", "mentalism", "emcee")


class Strict(BaseModel):
    model_config = ConfigDict(extra="ignore")


# --- auth ---------------------------------------------------------------
class LoginIn(Strict):
    email: str
    password: str


class TokenOut(Strict):
    access_token: str
    token_type: str = "bearer"
    user: dict


class PasswordChangeIn(Strict):
    currentPassword: str
    newPassword: str = Field(min_length=8, max_length=72)


# --- gallery ------------------------------------------------------------
class GalleryIn(Strict):
    type: MediaType = "image"
    category: GalleryCategory = "Stage Magic"
    title: str = ""
    description: str = ""
    mediaUrl: str = Field(min_length=1)
    thumbnailUrl: str = ""
    publicId: str = ""
    thumbnailPublicId: str = ""
    layout: GalleryLayout = "medium"
    status: PublishStatus = "published"
    sortOrder: int = 0


class GalleryPatch(Strict):
    type: MediaType | None = None
    category: GalleryCategory | None = None
    title: str | None = None
    description: str | None = None
    mediaUrl: str | None = None
    thumbnailUrl: str | None = None
    publicId: str | None = None
    thumbnailPublicId: str | None = None
    layout: GalleryLayout | None = None
    status: PublishStatus | None = None
    sortOrder: int | None = None


# --- testimonials -------------------------------------------------------
class TestimonialIn(Strict):
    clientName: str = ""
    company: str = ""
    role: str = ""
    eventType: str = ""
    rating: int = Field(default=0, ge=0, le=5)
    text: str = ""
    photoUrl: str = ""
    videoUrl: str = ""
    publicId: str = ""
    photoPublicId: str = ""
    status: PublishStatus = "published"
    sortOrder: int = 0


class TestimonialPatch(Strict):
    clientName: str | None = None
    company: str | None = None
    role: str | None = None
    eventType: str | None = None
    rating: int | None = Field(default=None, ge=0, le=5)
    text: str | None = None
    photoUrl: str | None = None
    videoUrl: str | None = None
    publicId: str | None = None
    photoPublicId: str | None = None
    status: PublishStatus | None = None
    sortOrder: int | None = None


# --- service images (the four core performance sections) ----------------
class ServiceImagePatch(Strict):
    imageUrl: str = Field(min_length=1)
    publicId: str = ""


# --- event packages -----------------------------------------------------
class PackageIn(Strict):
    title: str = Field(min_length=1)
    shortDescription: str = ""
    fullDescription: str = ""
    highlights: list[str] = Field(default_factory=list)
    imageUrl: str = ""
    publicId: str = ""
    ctaLabel: str = "Enquire Now"
    ctaLink: str = "/book"
    status: PublishStatus = "published"
    sortOrder: int = 0


class PackagePatch(Strict):
    title: str | None = None
    shortDescription: str | None = None
    fullDescription: str | None = None
    highlights: list[str] | None = None
    imageUrl: str | None = None
    publicId: str | None = None
    ctaLabel: str | None = None
    ctaLink: str | None = None
    status: PublishStatus | None = None
    sortOrder: int | None = None


# --- bookings -----------------------------------------------------------
class BookingIn(Strict):
    name: str = Field(min_length=1, max_length=120)
    mobile: str = Field(min_length=6, max_length=25)
    email: str = ""
    date: str = ""
    services: list[str] = Field(default_factory=list)
    duration: str = ""
    guests: int = Field(default=0, ge=0, le=1_000_000)
    venue: str = ""
    sound: str = ""
    location: str = ""
    message: str = ""


class BookingPatch(Strict):
    status: BookingStatus | None = None
    internalNote: str | None = None


# --- availability -------------------------------------------------------
class BlockedDateIn(Strict):
    """A single calendar day the artist is not available on. `date` is a plain
    YYYY-MM-DD string — no timezone maths, the same value the date input sends."""

    date: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")
    note: str = ""


class BlockedDatesIn(Strict):
    dates: list[str] = Field(default_factory=list, max_length=366)
    note: str = ""


# --- site settings ------------------------------------------------------
class SiteSettingsIn(Strict):
    artistName: str = "Maverick Manju"
    tagline: str = ""
    phone: str = ""
    whatsapp: str = ""
    email: str = ""
    instagram: str = ""
    facebook: str = ""
    youtube: str = ""
    website: str = ""
    defaultBookingMessage: str = ""
    footerCopyright: str = ""
    googleReviewLink: str = ""
    heroImageUrl: str = ""
    heroImagePublicId: str = ""
