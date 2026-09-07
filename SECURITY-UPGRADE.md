# Security dependency update — 2026-09-07

Use Node.js 22.12 or newer in the 22.x line, or Node.js 24+. Install with `npm ci` so the patched dependency versions in the lockfile are used.

Angular is updated to 21.2.22, the build tools to 21.2.23, and TypeScript to 5.9.3. The application keeps Zone-based change detection. The application builder replaces the old Webpack build dependencies. `qs` is pinned to 6.16.0 because the Karma dependency tree otherwise resolves a vulnerable version.

Validation: `npm ci`, `npm run build`, `npm test -- --watch=false --browsers=ChromeHeadless`, and `npm audit`. The dependency audit includes development dependencies and does not suppress advisories.

Run the frontend commands from `FRONTEND/hoteleriappClient`. jsPDF is updated to 4.2.1; a browser test checks the ticket image and PDF output.

## Backend

Use Python 3.12. From `BACKEND`, install `python -m pip install -r requirements.txt`. For validation, install `requirements-dev.txt`, then run `python -m pytest -q` and `python -m pip_audit -r requirements.txt`.

FastAPI, Werkzeug, multipart handling, Pillow and related runtime dependencies are updated. PyJWT replaces python-jose; unused passlib is removed. JWTs keep the existing signing key, algorithm and claims. Tests cover login with an existing PBKDF2 password hash, valid/invalid/expired tokens, profile serialization and QR images. Staff creation, admin creation and role changes now enforce administrator authentication on the server. Tests exercise both rejected requests and successful administrator operations. Token fragments are no longer printed.

Rebuild/redeploy the frontend and backend to apply these changes to a running service. Production data is not modified by the tests; they use a separate in-memory database. This dependency update is not a complete application security audit.
