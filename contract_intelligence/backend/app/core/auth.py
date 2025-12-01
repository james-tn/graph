# Copyright (c) Microsoft. All rights reserved.
"""
Azure AD JWT token validation for FastAPI.

This module provides middleware and dependencies for validating Azure AD JWT tokens
in the FastAPI application. It checks:
1. Token is from the expected AAD_FRONTEND_CLIENT_ID (azp claim)
2. Token audience matches AAD_API_AUDIENCE (aud claim)
3. Token is properly signed by Azure AD
4. Token has not expired

CROSS-TENANT AUTHENTICATION SUPPORT:
This implementation supports cross-tenant scenarios where the frontend app
and backend API app are registered in different Azure AD tenants:
- AAD_FRONTEND_TENANT_ID: Tenant where frontend app is registered
- AAD_API_TENANT_ID: Tenant where backend API app is registered (used for token validation)
- Token validation uses API tenant's signing keys and issuer
"""

import os
from typing import Optional
from fastapi import HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from jwt import PyJWKClient
import logging

logger = logging.getLogger(__name__)

# Environment variables
AAD_FRONTEND_TENANT_ID = os.getenv("AAD_FRONTEND_TENANT_ID")  # Frontend app's tenant
AAD_API_TENANT_ID = os.getenv("AAD_API_TENANT_ID")  # Backend API's tenant (for token validation)
AAD_API_AUDIENCE = os.getenv("AAD_API_AUDIENCE")
AAD_FRONTEND_CLIENT_ID = os.getenv("AAD_FRONTEND_CLIENT_ID")
DISABLE_AUTH = os.getenv("DISABLE_AUTH", "false").lower() == "true"

# Azure AD OpenID configuration (use API tenant for token validation)
JWKS_URL = f"https://login.microsoftonline.com/{AAD_API_TENANT_ID}/discovery/v2.0/keys"
ISSUER = f"https://login.microsoftonline.com/{AAD_API_TENANT_ID}/v2.0"

# HTTP Bearer token scheme
security = HTTPBearer(auto_error=False)


def validate_token(token: str) -> dict:
    """
    Validate Azure AD JWT token.
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded token payload
        
    Raises:
        HTTPException: If token is invalid
    """
    try:
        # Get signing keys from Azure AD
        jwks_client = PyJWKClient(JWKS_URL)
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        
        # Decode and validate token
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            audience=AAD_API_AUDIENCE,
            issuer=ISSUER,
            options={
                "verify_signature": True,
                "verify_exp": True,
                "verify_aud": True,
                "verify_iss": True,
            }
        )
        
        # Validate authorized party (azp) - should be the frontend client ID
        azp = payload.get("azp")
        if azp != AAD_FRONTEND_CLIENT_ID:
            logger.warning(f"Token azp claim '{azp}' does not match expected frontend client ID")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token: authorized party mismatch"
            )
        
        return payload
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidAudienceError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: audience mismatch (expected {AAD_API_AUDIENCE})"
        )
    except jwt.InvalidIssuerError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: issuer mismatch (expected {ISSUER})"
        )
    except jwt.InvalidTokenError as e:
        logger.error(f"Token validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error during token validation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service error"
        )


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security)
) -> Optional[dict]:
    """
    FastAPI dependency to extract and validate JWT token from Authorization header.
    
    Returns:
        Decoded token payload with user information, or None if auth is disabled
        
    Raises:
        HTTPException: If token is missing or invalid
    """
    # Skip authentication if disabled (development only)
    if DISABLE_AUTH:
        logger.warning("Authentication is DISABLED - skipping token validation")
        return None
    
    # Check if required AAD configuration is present
    if not all([AAD_API_TENANT_ID, AAD_API_AUDIENCE, AAD_FRONTEND_CLIENT_ID, AAD_FRONTEND_TENANT_ID]):
        logger.error("AAD configuration incomplete - cannot validate tokens")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication configuration error"
        )
    
    # Require Authorization header
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Extract token from "Bearer <token>"
    token = credentials.credentials
    
    # Validate and decode token
    payload = validate_token(token)
    
    return payload


def get_user_id(user: Optional[dict]) -> Optional[str]:
    """
    Extract user ID from decoded token payload.
    
    Args:
        user: Decoded token payload from get_current_user
        
    Returns:
        User object ID (oid claim) or None if auth is disabled
    """
    if user is None:
        return None
    return user.get("oid")


def get_user_email(user: Optional[dict]) -> Optional[str]:
    """
    Extract user email from decoded token payload.
    
    Args:
        user: Decoded token payload from get_current_user
        
    Returns:
        User email (preferred_username or email claim) or None if auth is disabled
    """
    if user is None:
        return None
    return user.get("preferred_username") or user.get("email")
