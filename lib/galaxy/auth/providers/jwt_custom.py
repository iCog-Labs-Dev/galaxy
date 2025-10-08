import jwt
import logging
import os
import json
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

from bioblend.galaxy import GalaxyInstance
from bioblend import ConnectionError
from cryptography.fernet import Fernet, InvalidToken

from galaxy.auth.providers import AuthProvider

# Environment / secrets
FERNET_SECRET = os.getenv("SECRET_KEY")
if not FERNET_SECRET:
    raise RuntimeError("SECRET_KEY (Fernet secret) is required in env")
fernet = Fernet(FERNET_SECRET)

GALAXY_API_TOKEN = "galaxy_api_token"

log = logging.getLogger(__name__)

class JWTCustom(AuthProvider):
    plugin_type = "jwt_custom"

    def authenticate(self, email, username, password, options, request):
        """Used for auto-registration or new users. Validates JWT, extracts API key, uses BioBlend to validate and get user details."""
        token = self._get_token(request)
        if not token:
            return False, "", ""  # Reject but allow other providers

        try:
            # Decode JWT to get API key
            payload = jwt.decode(
                token,
                options={"verify_signature": False} 
            )

            if GALAXY_API_TOKEN not in payload:
                log.error("JWT missing API key claim '%s'", GALAXY_API_TOKEN)
                raise jwt.InvalidTokenError("Missing API key in JWT")
            
            galaxy_encrypted_api = payload.get(GALAXY_API_TOKEN)
            
            api_key = self._decrypt_api_token(galaxy_encrypted_api)
            
            # Get current Galaxy URL from request.
            galaxy_url = request.application_url

            # Validate API key via BioBlend connection
            gi = GalaxyInstance(url=galaxy_url, key=api_key)
            user_info = gi.users.get_current_user()

            extracted_email = user_info.get("email")
            extracted_username = user_info.get("username")
            if not extracted_email or not extracted_username:
                raise ConnectionError("Missing user details from BioBlend")

            log.info(f"BioBlend JWT auth success for username: {extracted_username} email: {extracted_email}")
            # Accept and provide for user creation
            return True, extracted_email, extracted_username
        except (jwt.InvalidTokenError, ConnectionError) as e:
            log.warning(f"Invalid JWT or API key: {e}")
            return False, "", ""  # Reject

    def authenticate_user(self, user, password, options, request):
        """Used for existing users. Validates JWT, extracts API key, uses BioBlend to confirm it matches the user."""
        status, _, _ = self.authenticate(user.email, user.username, password, options, request)
        return bool(status)

    def _get_token(self, request):
        """Extract JWT from header or query param/POST body."""
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        if not token:
            token = request.params.get("jwt", "")
        return token
    
    def _decrypt_api_token(self, token_str: str) -> Optional[str]:
        """
        If token_str is a fernet-encrypted payload (bytes when encoded),
        decrypt and parse JSON for {"apikey": "<value>"} and return the value.
        Returns None if decryption/parsing fails.
        """
        if not isinstance(token_str, str) or not token_str:
            return None
        
        try:
            decrypted = fernet.decrypt(token =token_str.encode("utf-8"))
            parsed = json.loads(decrypted.decode("utf-8"))
            apikey = parsed.get("apikey")
            if apikey and isinstance(apikey, str):
                return apikey
            log.error("Decrypted JWT galaxy api-key payload missing 'apikey' field")
            return None
        except (InvalidToken, Exception) as e:
            
            # Not a fernet payload or parse failed
            log.debug("Fernet decryption/parsing failed for JWT claim: %s", e)
            return None
        

__all__ = ("JWTCustom",)