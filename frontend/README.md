# E-Commerce LLM Frontend

This is a repository that contains the frontend part of the system.

## Getting started

1. Install nodejs (20+) and [pnpm](https://pnpm.io/) on your machine 
2. Run `pnpm install`
3. Set `VITE_API_BASE` env variable to point to your backend (e.g. `VITE_API_BASE=http://localhost:8000`)
4. Make sure that your backend instance has the CORS headers set correctly (i.e. set `ECL_DJANGO_CORS_ALLOWED_ORIGINS=["http://localhost:5173"]`) 
5. To develop locally run `pnpm run dev`

## Building the application

1. Run `pnpm build`
