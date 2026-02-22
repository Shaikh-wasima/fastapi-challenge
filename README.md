# Challenge Platform Backend (FastAPI + SQLite)

Simple backend service for a challenge platform with authentication, challenge management, joining, and progress tracking.

## Setup Instructions
1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Ensure MongoDB is running (local or remote).
4. Create a `.env` file (see `.env.example`) and set at least `SECRET_KEY` and `MONGODB_URL`.
   - If Mongo requires auth, include credentials in `MONGODB_URL`.
   - You can disable index creation with `MONGODB_CREATE_INDEXES=false`.

5. Run the API:

```bash
uvicorn app.main:app --reload
```

MongoDB will create the database and collections automatically on first write.

## How Authentication Works
Token-based authentication using JWT (Bearer tokens).
- Register: `POST /auth/register` with JSON body `{ "email": "...", "password": "..." }`
- Login: `POST /auth/login` using form data `username` (email) and `password`
- Protected endpoints require `Authorization: Bearer <token>`

## Data Model Overview
- `users`
  - `id`, `email`, `password_hash`, `created_at`
- `challenges`
  - `id`, `title`, `description`, `target_value`, `duration_days`, `is_active`, `created_at`
- `user_challenges`
  - `id`, `user_id`, `challenge_id`, `joined_at`, `progress`
  - Unique constraint on (`user_id`, `challenge_id`) to prevent joining twice

## API Summary
- `POST /auth/register` (public)
- `POST /auth/login` (public)
- `POST /challenges` (protected)
- `GET /challenges` (public; only active)
- `POST /challenges/{challenge_id}/join` (protected)
- `POST /progress` (protected)

## Comments
- Uses MongoDB via Motor (async driver).
- `SECRET_KEY` should be set to a secure value for production.
