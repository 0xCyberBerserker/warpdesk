# Branding and Icons

WarpDesk uses two icon layers:

- a custom WarpDesk launcher icon for menu / desktop branding
- Cloudflare status icons for connection-state signaling inside the app

Included assets:

- `assets/warpdesk-shield.svg`
- `assets/cloudflare-zero-trust-orange.svg`
- `assets/cloudflare-zero-trust-connected.svg`
- `assets/cloudflare-zero-trust-disconnected.svg`
- `assets/cloudflare-zero-trust-error.svg`

## Custom launcher icon

The launcher icon is the WarpDesk shield:

- shield: security / privacy
- bolt / tunnel stroke: speed / connection
- blue-violet gradient: distinct app identity instead of reusing Cloudflare orange as the main launcher brand

The original SVG needed one technical correction before being usable:

- `xmlns="http://w3.org"` was invalid and has been corrected to `xmlns="http://www.w3.org/2000/svg"`

## Source

Cloudflare status icons were taken from the locally installed Cloudflare WARP package on this machine:

```text
/usr/share/icons/hicolor/scalable/apps/
```

and:

```text
/usr/share/warp/images/
```

## Important note

If you publish this repository publicly, Cloudflare trademarks and brand assets are Cloudflare's.

Practical implication:

- local personal use: fine
- public GitHub repo / releases: treat the Cloudflare status assets as third-party brand material

The current setup is safer than before because the main launcher identity is now WarpDesk's own icon rather than a Cloudflare launcher icon.
