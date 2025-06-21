#!/bin/sh

pnpm build

pnpm exec vite preview --host 0.0.0.0 --port $PORT
