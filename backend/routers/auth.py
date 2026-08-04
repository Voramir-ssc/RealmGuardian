from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import time
import models
from dependencies import get_db, get_blizzard_client
from config import config
from background_tasks import sync_user_characters

router = APIRouter(prefix="/api/auth", tags=["Auth"])

@router.get('/login')
def login(request: Request, tab: str = "settings"):
    """
    Initiates the Battle.net OAuth2 login flow.
    Passes the user's active frontend tab in the `state` parameter so they are returned
    to the correct page after authentication.
    """
    blizzard_client = get_blizzard_client()
    host = request.headers.get("host", "localhost:8000")
    base_url = f"http://{host}"
    redirect_uri = f"{base_url}/api/auth/callback"
    url = blizzard_client.get_authorization_url(redirect_uri, state=tab)
    return RedirectResponse(url)

@router.get('/callback')
def auth_callback(code: str, state: str, background_tasks: BackgroundTasks, request: Request, db: Session = Depends(get_db)):
    """
    OAuth2 Callback Endpoint: Handles the response from Battle.net.
    Exchanges the authorization code for an access token, triggers a background character sync,
    and redirects the user back to the React frontend with its active tab restored.
    """
    blizzard_client = get_blizzard_client()
    host = request.headers.get("host", "localhost:8000")
    base_url = f"http://{host}"
    redirect_uri = f"{base_url}/api/auth/callback"
    token_data = blizzard_client.exchange_code_for_token(code, redirect_uri)
    
    if not token_data or "access_token" not in token_data:
        raise HTTPException(status_code=400, detail="Failed to retrieve user token")

    user_token = token_data["access_token"]
    expires_in = token_data.get("expires_in", 86400)

    # Save token for automatic background sync
    db.query(models.UserAccessToken).delete()
    new_token = models.UserAccessToken(
        access_token=user_token, 
        expires_at=int(time.time() + expires_in)
    )
    db.add(new_token)
    db.commit()

    # Start background sync
    background_tasks.add_task(sync_user_characters, user_token)
    
    # Redirect immediately to dynamic frontend host
    host = request.headers.get("host", "localhost")
    hostname = host.split(":")[0]
    return RedirectResponse(f"http://{hostname}:5173?connected=true&tab={state}")
