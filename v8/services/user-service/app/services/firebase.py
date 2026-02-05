"""Firebase authentication service."""

from typing import Optional


class FirebaseAuthStub:
    """Stub implementation of Firebase authentication."""

    async def verify_token(self, token: str) -> dict:
        """
        Verify Firebase ID token.
        This is a stub implementation for development.

        In production, this would:
        1. Verify the Firebase ID token using firebase_admin
        2. Extract user information from the token
        3. Return user data

        Args:
            token: Firebase ID token

        Returns:
            dict: User information from Firebase

        Raises:
            HTTPException: If token is invalid
        """
        # Mock Firebase user data
        return {
            "uid": "firebase_mock_uid_123",
            "email": "user@example.com",
            "email_verified": True,
            "display_name": "Mock Firebase User",
            "photo_url": "https://example.com/photo.jpg",
        }


# Singleton instance
_firebase_auth = FirebaseAuthStub()


async def verify_token(token: str) -> dict:
    """
    Verify Firebase ID token and return user information.

    Args:
        token: Firebase ID token

    Returns:
        dict: User information from Firebase
    """
    return await _firebase_auth.verify_token(token)


def init_firebase(credentials_path: Optional[str] = None, project_id: Optional[str] = None):
    """
    Initialize Firebase Admin SDK.
    This is a stub for development.

    In production, this would:
    1. Load Firebase credentials
    2. Initialize firebase_admin
    3. Set up Firebase Auth

    Args:
        credentials_path: Path to Firebase credentials JSON file
        project_id: Firebase project ID
    """
    # TODO: Implement Firebase initialization
    # import firebase_admin
    # from firebase_admin import credentials, auth
    #
    # if credentials_path:
    #     cred = credentials.Certificate(credentials_path)
    #     firebase_admin.initialize_app(cred, {'projectId': project_id})
    pass
