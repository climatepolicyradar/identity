from fastapi import Depends, FastAPI

from .auth import AuthenticatedUser, get_current_user

app = FastAPI()


@app.get("/me")
def get_me(user: AuthenticatedUser = Depends(get_current_user)):
    """Returns the current user's profile. 401 if the token is missing or invalid."""
    return {"sub": user.sub, "email": user.email, "name": user.name}


@app.get("/health")
def health():
    """Public endpoint — no auth required."""
    return {"status": "ok"}
