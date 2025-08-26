import secrets
from typing import Any
import dotenv
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
import os
from msal import ConfidentialClientApplication

dotenv.load_dotenv()

MICROSOFT_TENANT_ID = os.getenv("MICROSOFT_TENANT_ID", "common")
MICROSOFT_CLIENT_ID = os.getenv("MICROSOFT_CLIENT_ID", None)
if not MICROSOFT_CLIENT_ID:
    raise ValueError("MICROSOFT_CLIENT_ID environment variable is not set.")
MICROSOFT_CLIENT_SECRET = os.getenv("MICROSOFT_CLIENT_SECRET", None)
if not MICROSOFT_CLIENT_SECRET:
    raise ValueError("MICROSOFT_CLIENT_SECRET environment variable is not set.")

client_app = ConfidentialClientApplication(
    client_id=MICROSOFT_CLIENT_ID,
    client_credential=MICROSOFT_CLIENT_SECRET,
    authority=f"https://login.microsoftonline.com/{MICROSOFT_TENANT_ID}",
)


def get_auth_url_and_state(request: Request) -> str:
    # Generate a random state for CSRF protection and session tracking
    state = secrets.token_urlsafe(32)

    # Store state in session for verification later
    request.session["oauth_state"] = state

    # Build the authorization URL
    auth_flow = client_app.initiate_auth_code_flow(
        scopes=["User.Read"],
        redirect_uri="http://localhost:9090/api/callback",
        state=state,
    )

    # Store the auth flow in session (contains code_verifier, etc.)
    request.session["auth_flow"] = auth_flow

    return auth_flow["auth_uri"]


def exchange_code_for_token(request: Request, code: str, state: str) -> dict[str, Any]:
    """Exchange authorization code for access token.

    Args:
        request: FastAPI request object
        code: Authorization code from Microsoft
        state: State parameter for CSRF protection

    Returns:
        Token response with user info

    Raises:
        HTTPException: If token exchange fails
    """
    # Verify state matches what we stored
    stored_state = request.session.get("oauth_state")
    if not stored_state or stored_state != state:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid state parameter",
        )

    # Get the auth flow we stored during initiation
    auth_flow = request.session.get("auth_flow")
    if not auth_flow:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No auth flow found in session",
        )

    # Exchange code for token
    result = client_app.acquire_token_by_auth_code_flow(
        auth_code_flow=auth_flow, auth_response={"code": code, "state": state}
    )

    # Clean up session state after use (security best practice)
    request.session.pop("oauth_state", None)
    request.session.pop("auth_flow", None)

    if "error" in result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token exchange failed",  # Don't expose detailed error in production
        )

    return result


app: FastAPI = FastAPI()


app.add_middleware(
    SessionMiddleware,
    secret_key="my_secret_key",
    session_cookie="session",
    https_only=True,
)


@app.get("/api/login")
async def login(request: Request) -> RedirectResponse:
    request.session["my-cookie"] = "cookie-value"
    return RedirectResponse(url=get_auth_url_and_state(request))


@app.get("/api/callback")
async def callback(request: Request, code: str, state: str) -> RedirectResponse:
    token = exchange_code_for_token(request, code, state)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token exchange failed",
        )
    print("Access token:", token.get("access_token"))
    return RedirectResponse(url="http://localhost:9090/")


# Mount static files for the React client
client_build_path = os.path.join(os.path.dirname(__file__), "../client/dist")
if os.path.exists(client_build_path):
    app.mount("/", StaticFiles(directory=client_build_path, html=True), name="static")


def main():
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=9090)


if __name__ == "__main__":
    main()
