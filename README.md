# Demonstration of failure of Cypress after Microsoft login redirect

## Setup

1. Copy `.env.sample` to `.env` and fill in the required values. This will require Microsoft Entra access. The user will need to have MFA disabled for this demo to work.
2. Install [uv](https://docs.astral.sh/uv/getting-started/installation/) if you don't have it already.
3. `uv sync` to install Python dependencies.
4. `cd client && npm install` to install client dependencies.

## Running the App

1. `make start` to start the FastAPI server and open the Cypress test runner.
2. In the Cypress test runner, select the `try-with-cookie.cy.ts` test to run it.

## Structural Overview

### Auth flow overview

If you're not familiar with OAuth2/OIDC, here's a quick overview of the auth flow:

1. The user clicks "Login" and they hit the backend `/api/login` endpoint. This returns a `set-cookie` for a `session` cookie with OAuth state saved to it
to prevent CSRF. It generates a microsoft login URL that will re-direct them back to our backend `/api/auth/callback` endpoint after they login.
2. The server redirects them to that URL.
3. They log in, microsoft calls the redirect URL with a `code` and `state` query parameter.
4. The backend `/api/auth/callback` endpoint verifies the `state` against the `oauth_state` value stored in the session cookie from the first step.
5. The backend exchanges the `code` for for a auth token from Microsoft using the python MSAL library. In real life, we would store use this token to look up a user.

### Components

- `backend/` - FastAPI backend with the OAuth2/OIDC auth flow implemented. It has the following endpoints:
  - `GET /api/login` - Starts the login process by generating a microsoft login URL and setting a session cookie.
  - `GET /api/auth/callback` - Handles the redirect from microsoft after login, verifies state, and exchanges code for token.
  - `GET /` - Serves the frontend app.
- `client/` - Basic React frontend app that has a login button that hits the backend's `/api/login` endpoint.

## Note about Playwright

Please ignore some of the commented-out code in `backend/main.py`. Bypassing real auth is the only way to get
the test to pass in Cypress. Playwright does not need this bypass and can use the real auth code flow.
