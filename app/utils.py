import requests
from django.conf import settings


def verify_turnstile_token(token, remote_ip=None):
    """
    Verify Cloudflare Turnstile token
    
    Args:
        token (str): The Turnstile token from the form
        remote_ip (str, optional): The user's IP address
    
    Returns:
        bool: True if token is valid, False otherwise
    """
    if not token:
        return False
    
    data = {
        'secret': settings.TURNSTILE_SECRET_KEY,
        'response': token,
    }
    
    if remote_ip:
        data['remoteip'] = remote_ip
    
    try:
        response = requests.post(
            'https://challenges.cloudflare.com/turnstile/v0/siteverify',
            data=data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get('success', False)
        
    except requests.RequestException:
        pass
    
    return False


def get_client_ip(request):
    """
    Get the client's IP address from the request
    
    Args:
        request: Django request object
    
    Returns:
        str: The client's IP address
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
