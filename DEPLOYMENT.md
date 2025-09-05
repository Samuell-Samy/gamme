# Vercel Deployment Guide for Django

## Issues Fixed

1. **Database Configuration**: Updated to use PostgreSQL for production (Vercel) and SQLite for local development
2. **Static Files**: Configured WhiteNoise for proper static file serving on Vercel
3. **Environment Variables**: Added proper environment variable handling
4. **Vercel Configuration**: Updated `vercel.json` for proper Django deployment
5. **Dependencies**: Added missing `dj-database-url` and `psycopg2-binary` packages

## Required Environment Variables

Set these in your Vercel dashboard:

1. **SECRET_KEY**: Generate a new Django secret key
   ```bash
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

2. **DEBUG**: Set to `False` for production

3. **DATABASE_URL**: PostgreSQL connection string (Vercel will provide this if you add a PostgreSQL database)

## Database Setup

### Option 1: Use Vercel PostgreSQL (Recommended)
1. Go to your Vercel project dashboard
2. Navigate to the "Storage" tab
3. Create a new PostgreSQL database
4. Vercel will automatically set the `DATABASE_URL` environment variable

### Option 2: Use External Database
1. Set up a PostgreSQL database (e.g., on Railway, Supabase, or Neon)
2. Add the connection string as `DATABASE_URL` environment variable

## Deployment Steps

1. **Rename requirements file** (if not already done):
   ```bash
   mv requirments.txt requirements.txt
   ```

2. **Install dependencies locally** (optional, for testing):
   ```bash
   pip install -r requirements.txt
   ```

3. **Run migrations** (after setting up database):
   ```bash
   python manage.py migrate
   ```

4. **Deploy to Vercel**:
   ```bash
   vercel --prod
   ```

## File Structure Changes

- Created `api/index.py` for Vercel serverless function
- Updated `vercel.json` configuration
- Added `.vercelignore` file
- Updated Django settings for production

## Testing Locally

To test the Vercel configuration locally:

```bash
vercel dev
```

This will simulate the Vercel environment locally.

## Troubleshooting

If you still get errors:

1. Check Vercel function logs in the dashboard
2. Ensure all environment variables are set
3. Verify the database connection
4. Check that all dependencies are in `requirements.txt`
