import jwt
import requests
from django.conf import settings
from django.contrib.auth.models import AnonymousUser, User
from rest_framework import authentication, exceptions
from jose import jwt as jose_jwt
from jose.exceptions import JWTError, ExpiredSignatureError, JWTClaimsError
import json


class KeycloakUser:
    """Custom user class for Keycloak JWT token"""
    def __init__(self, token_payload):
        self.token_payload = token_payload
        self.username = token_payload.get('preferred_username', '')
        self.email = token_payload.get('email', '')
        self.first_name = token_payload.get('given_name', '')
        self.last_name = token_payload.get('family_name', '')
        self.is_authenticated = True
        self.is_active = True
        self.is_anonymous = False
        self.pk = token_payload.get('sub', '')
        self.id = self.pk

    def __str__(self):
        return self.username


class KeycloakJWTAuthentication(authentication.BaseAuthentication):
    """
    JWT authentication using Keycloak public key
    """
    
    def __init__(self):
        self.keycloak_public_key = None
        self.key_cache_timeout = 3600  # Cache for 1 hour
        self.last_key_fetch = 0
    
    def get_keycloak_public_key(self):
        """
        Fetch and cache Keycloak public key
        """
        import time
        current_time = time.time()
        
        # Return cached key if still valid
        if (self.keycloak_public_key and 
            current_time - self.last_key_fetch < self.key_cache_timeout):
            return self.keycloak_public_key
        
        try:
            # Fetch JWKS from Keycloak
            response = requests.get(settings.KEYCLOAK_CERT_URL, timeout=10)
            response.raise_for_status()
            jwks = response.json()
            
            # Get the first key (usually there's only one)
            if 'keys' in jwks and len(jwks['keys']) > 0:
                key_data = jwks['keys'][0]
                
                # Store the JWKS for use with python-jose
                self.keycloak_public_key = jwks
                self.last_key_fetch = current_time
                
                return self.keycloak_public_key
            else:
                raise exceptions.AuthenticationFailed('No keys found in JWKS')
                
        except requests.RequestException as e:
            raise exceptions.AuthenticationFailed(f'Failed to fetch Keycloak public key: {str(e)}')
        except Exception as e:
            raise exceptions.AuthenticationFailed(f'Error processing Keycloak public key: {str(e)}')
    
    def authenticate(self, request):
        """
        Authenticate the request and return a two-tuple of (user, token).
        """
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        
        if not auth_header:
            return None
        
        try:
            # Extract token from "Bearer <token>"
            prefix, token = auth_header.split(' ', 1)
            if prefix.lower() != 'bearer':
                return None
        except ValueError:
            return None
        
        try:
            # Get Keycloak JWKS
            jwks = self.get_keycloak_public_key()
            
            # Decode and verify JWT token using JWKS
            payload = jose_jwt.decode(
                token,
                jwks,  # Pass JWKS directly
                algorithms=['RS256'],
                audience=None,  # Skip audience validation for now
                options={
                    'verify_aud': False,  # Skip audience verification
                    'verify_exp': True,   # Verify expiration
                    'verify_iat': True,   # Verify issued at
                    'verify_nbf': True,   # Verify not before
                }
            )
            
            # Create user from token payload
            user = KeycloakUser(payload)
            
            return (user, token)
            
        except ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('Token has expired')
        except JWTClaimsError as e:
            raise exceptions.AuthenticationFailed(f'Invalid token claims: {str(e)}')
        except JWTError as e:
            raise exceptions.AuthenticationFailed(f'Invalid token: {str(e)}')
        except Exception as e:
            raise exceptions.AuthenticationFailed(f'Authentication failed: {str(e)}')
    
    def authenticate_header(self, request):
        """
        Return a string to be used as the value of the `WWW-Authenticate`
        header in a `401 Unauthenticated` response.
        """
        return 'Bearer realm="keycloak"'