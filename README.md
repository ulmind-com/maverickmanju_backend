# Maverick Manju API

FastAPI backend for the [Maverick Manju website](https://github.com/ulmind-com/maverickmanju_website)
— gallery, testimonials, service images, event packages, booking enquiries,
site settings and admin auth.

- **Runtime:** Python 3.11+, managed with [uv](https://docs.astral.sh/uv/)
- **Database:** MongoDB Atlas (async driver: `pymongo.AsyncMongoClient`)
- **Media:** Cloudinary (images and video, uploaded through the API)
- **Auth:** JWT bearer tokens, bcrypt password hashing

## Run it

```bash
cd backend
cp .env.example .env   # fill in Mongo, Cloudinary and JWT values
uv sync
uv run uvicorn app.main:app --reload --port 8000
```

Interactive docs: <http://localhost:8000/docs>

On first boot the app creates its indexes and seeds the admin account, the four
service-image records, the six starter event packages and the site settings
document. Seeding is idempotent — nothing you edit later is overwritten.

## Environment

| Variable | Purpose |
| --- | --- |
| `MONGODB_URI` / `MONGODB_DB` | Atlas connection string and database name |
| `CLOUDINARY_CLOUD_NAME` / `_API_KEY` / `_API_SECRET` | Cloudinary credentials |
| `CLOUDINARY_FOLDER` | Root folder for uploads (default `maverickmanju`) |
| `JWT_SECRET` | Signing key — generate with `openssl rand -base64 48` |
| `JWT_EXPIRE_MINUTES` | Session lifetime (default 7 days) |
| `ADMIN_EMAIL` / `ADMIN_PASSWORD` / `ADMIN_NAME` | Seeded on first boot only |
| `CORS_ORIGINS` | Comma-separated allowed origins |
| `CORS_ORIGIN_REGEX` | Regex for preview/production domains |
| `MAX_UPLOAD_MB` | Rejects larger uploads (default 100) |

`ADMIN_PASSWORD` only applies when the account does not exist yet. Afterwards
change it from **Admin → Settings → Admin password**.

## Endpoints

Public (no auth):

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/api/gallery` | Published gallery items |
| `GET` | `/api/testimonials` | Published testimonials |
| `GET` | `/api/service-images` | Images for the four core performances |
| `GET` | `/api/packages` | Published event packages |
| `GET` | `/api/settings` | Contact details and socials |
| `POST` | `/api/bookings` | Booking form submission |
| `GET` | `/api/health` | Health check (pings Mongo) |

Admin (`Authorization: Bearer <token>`):

| Method | Path | Purpose |
| --- | --- | --- |
| `POST` | `/api/auth/login` | Exchange credentials for a token |
| `GET` | `/api/auth/me` | Current admin |
| `POST` | `/api/auth/change-password` | Rotate the password |
| `GET/POST/PATCH/DELETE` | `/api/admin/gallery[/{id}]` | Gallery CRUD |
| `GET/POST/PATCH/DELETE` | `/api/admin/testimonials[/{id}]` | Testimonial CRUD |
| `GET/POST/PATCH/DELETE` | `/api/admin/packages[/{id}]` | Event package CRUD |
| `GET/PUT` | `/api/admin/service-images[/{slug}]` | Swap a core section image |
| `GET/PATCH/DELETE` | `/api/admin/bookings[/{id}]` | Enquiry management |
| `PUT` | `/api/admin/settings` | Site settings |
| `POST` | `/api/admin/uploads` | Upload one image/video to Cloudinary |

Deleting a record also deletes its Cloudinary asset, so the media library does
not accumulate orphans.

## Collections

`gallery_items`, `testimonials`, `service_images`, `event_packages`,
`bookings`, `site_settings`, `admin_users`, `counters` (booking reference
sequence).

## Deploying to Render

`render.yaml` is a ready-made blueprint. Either **New → Blueprint** and point it
at this repo, or create a **Web Service** manually with:

| Setting | Value |
| --- | --- |
| Runtime | Python |
| Build command | `pip install uv && uv sync --frozen --no-dev` |
| Start command | `uv run uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| Health check path | `/api/health` |

`.python-version` pins Python 3.12 and uv fetches that interpreter itself, so
the build does not depend on which Python the Render image ships with.

Then set the environment variables from the table above in **Environment** —
`MONGODB_URI`, the three `CLOUDINARY_*` values, `JWT_SECRET`, `ADMIN_EMAIL`,
`ADMIN_PASSWORD` and `CORS_ORIGINS`. Nothing is read from `.env` in production;
that file is git-ignored and only used locally.

Two things to get right:

1. **`CORS_ORIGINS`** must contain the site's origin, e.g.
   `https://maverickmanju-website.vercel.app,https://maverickmanju.in`.
   Preview deployments are already covered by `CORS_ORIGIN_REGEX`.
2. **MongoDB Atlas → Network Access** must allow Render's outbound IPs. On the
   free plan the simplest option is `0.0.0.0/0`; on a paid plan use Render's
   static outbound IPs.

Finally point the frontend at the deployed URL by setting `VITE_API_URL` in
Vercel, e.g. `https://maverickmanju-api.onrender.com`.

> On Render's free plan the service sleeps after inactivity, so the first
> request after a while takes ~30s to wake up.

## Deploying anywhere else

Any Python host works — Railway, Fly.io, a VPS:

```bash
uv sync --frozen --no-dev
uv run uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Set every variable from the environment table, and never ship `.env`.
