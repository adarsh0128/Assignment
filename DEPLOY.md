# Deployment

## Backend on Render

1. Create a Render Blueprint from this repository and select `render.yaml`.
2. Set `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS`, `DJANGO_CSRF_TRUSTED_ORIGINS`, and `CORS_ALLOWED_ORIGINS`.
3. Let Render provision the PostgreSQL database declared in the blueprint.
4. Open a Render shell and run:

```bash
python manage.py migrate
python manage.py createsuperuser
```

5. Register organization, facilities, plant mappings, data sources, and emission factors through the Django admin or a seed command.

## Frontend on Vercel

1. Import the repository in Vercel.
2. Set the project root to `frontend`.
3. Set `VITE_API_BASE_URL` to the Render backend URL ending in `/api/v1`.
4. Deploy with the default Vite build command from `vercel.json`.

## Environment Checklist

- `DJANGO_SECRET_KEY`
- `DJANGO_ALLOWED_HOSTS`
- `DJANGO_CSRF_TRUSTED_ORIGINS`
- `CORS_ALLOWED_ORIGINS`
- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_HOST`
- `POSTGRES_PORT`
- `VITE_API_BASE_URL`

## Production Differences

Local filesystem upload storage is used for prototype scope. Production should move uploaded source files to S3-compatible object storage with lifecycle policies, server-side encryption, and retention rules. Ingestion should run asynchronously with a queue so large CSV files do not occupy web workers.
