# Getting Started With Enthusiast Docs Setup

This guide walks you through to setup and run the Enthusiast documentation locally.

Using this guide you can preview your changes and give better contribution to the Enthusiast documentation.

## Install pnpm

This project uses [`pnpm`](https://pnpm.io/) as its package manager.

To install `pnpm` run:

```bash
npm install -g pnpm
```

On **macOS** or **Linux**, if you get `EACCES: permission denied error`, re-run it with sudo:

```bash
sudo npm install -g pnpm
```

## Install Dependencies

From the project root, install all dependencies:

```bash
pnpm dev
```

## Start the Development Server

To start the server, run:

```bash
pnpm dev
```

You should see output similar to:

```bash
✔ Ready in 2s
```

## Preview Docs in Browser

By default, the docs are served at **`http://localhost:3000/tools/enthusiast/docs/`**

> **Note**
>
> If you open [`http://localhost:3000/`](http://localhost:3000/), you’ll get a 404 page. Ensure to include `/tools/enthusiast/docs/` in the URL.

---

For common setup issues (missing `pnpm`, permission errors, 404s), see the [Troubleshooting guide](troubleshooting.md).

---

With these steps, you should have the Enthusiast docs running smoothly on your local machine.
