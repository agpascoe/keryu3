def get_location_from_ip(ip_address):
    """Get location string from IP address."""
    if not ip_address or ip_address == '127.0.0.1':
        return 'Local Test'
        
    try:
        # For now return a simple string with the IP
        # TODO: Integrate with IP geolocation service if needed
        return f'Scan from {ip_address}'
    except Exception as e:
        logger.error(f'Error getting location from IP {ip_address}: {str(e)}')
        return 'Unknown Location' 