import requests
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def weather_bangkok(request):
    """
    Get weather information for Bangkok from goweather.xyz API
    Requires JWT authentication from Keycloak
    """
    try:
        # Call external weather API
        weather_response = requests.get(
            'https://goweather.xyz/weather/bangkok',
            timeout=10
        )
        weather_response.raise_for_status()
        weather_data = weather_response.json()
        
        # Add user information from JWT token
        user_info = {
            'username': request.user.username,
            'email': request.user.email,
            'user_id': request.user.pk,
        }
        
        # Combine weather data with user info
        response_data = {
            'user': user_info,
            'weather': weather_data,
            'location': 'Bangkok',
            'message': 'Weather data retrieved successfully'
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except requests.RequestException as e:
        return Response(
            {
                'error': 'Failed to fetch weather data',
                'detail': str(e)
            },
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    except Exception as e:
        return Response(
            {
                'error': 'Internal server error',
                'detail': str(e)
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """
    Get current user profile information from JWT token
    """
    user_data = {
        'user_id': request.user.pk,
        'username': request.user.username,
        'email': request.user.email,
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
        'is_authenticated': request.user.is_authenticated,
        'token_payload': getattr(request.user, 'token_payload', {})
    }
    
    return Response({
        'user': user_data,
        'message': 'User profile retrieved successfully'
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([])  # No authentication required
def health_check(request):
    """
    Health check endpoint - no authentication required
    """
    return Response({
        'status': 'healthy',
        'message': 'Django API is running',
        'version': '1.0.0'
    }, status=status.HTTP_200_OK)