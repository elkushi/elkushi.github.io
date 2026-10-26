# elkushi.github.io

My portfolio site: [moustafa.dev → elkushi.github.io](https://elkushi.github.io).

Plain HTML and CSS. No framework, no build dependencies, no tracking, no
cookies, no external requests — every asset is served from this repo.

## Structure

```
content/      page fragments (the part that changes)
tools/build.py  wraps each fragment in the shared head, nav and footer
index.html    built output — do not edit by hand
work/         built case studies
style.css     one stylesheet
reveal.js     fades sections in on scroll; without JS everything is visible
```

## Rebuild and deploy

Deploys are automatic. Every push to `main` runs `.github/workflows/deploy.yml`: it builds the
pages from `content/`, checks every link, asset and the CSP (`tools/check.py`), and publishes to
GitHub Pages. A broken link stops the deploy.

```bash
python3 tools/build.py    # build locally
python3 tools/check.py    # same check the deploy runs
```

## Security

The pages ship a content security policy with `default-src 'none'`. Scripts are
limited to this origin plus one SHA-256 hash for the single inline bootstrap
line, so `'unsafe-inline'` is not needed for scripts. `base-uri` and
`form-action` are set to `'none'`. `build.py` computes the hash at build time,
so it can't drift from the script it allows.
