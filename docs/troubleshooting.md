# Troubleshooting

This guide covers common issues you may encounter when [setting up and running the Enthusiast documentation locally](README.md).

## 1. `pnpm: command not found`

**Cause:** pnpm is not installed.  
**Fix:** Install pnpm globally:

```bash
npm install -g pnpm
```

Or use Corepack:

```bash
corepack enable
corepack prepare pnpm@latest --activate
```

For more details on Corepack installation, refer to the official [Pnpm.io docs](https://pnpm.io/installation#using-corepack).

## 2. `EACCES: permission denied when installing pnpm`

**Cause**: You don’t have permission to write to /usr/local/lib when installing global npm packages.
**Fix**: Re-run with sudo:

```bash
sudo npm install -g pnpm
```

Or permanently fix permissions by following the [official npm guide](https://docs.npmjs.com/resolving-eacces-permissions-errors-when-installing-packages-globally).

## 3. 404 error on [`http://localhost:3000`](http://localhost:3000)

**Cause**: The docs are served with a base path.
**Fix**: Use the correct URL for docs:

[`http://localhost:3000/tools/enthusiast/docs/`](http://localhost:3000/tools/enthusiast/docs/)

## 4. Sidebar or homepage not showing

**Cause**: `_meta.ts` is missing proper labels for the docs.
**Fix**: Ensure it includes at least:

```ts
const mapping = {
  index: "Introduction",
  "getting-started": "Getting Started",
  customization: "Customization",
  agents: "Agents",
  management: "Management",
  integrate: "Integrations",
  observe: "Observability",
  plugins: "Plugins",
};

export default mapping;
```

With these fixes, most setup and onboarding issues should be resolved. If you encounter new errors, please open an [issue on GitHub](https://github.com/upsidelab/enthusiast/issues) so we can improve this guide.
