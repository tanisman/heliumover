from flask import request
from model.proxy_group import proxy_group
from model.hotspot import hotspot
from functools import wraps

def get_x_api_key():
    return request.headers.get('X-API-Key')

def authorize_hotspot(handler_function):
    @wraps(handler_function)

    def decorator(*args, **kwargs):
        hotspot_address = kwargs["hotspot_address"]
        
        has_correct_api_key = \
            hotspot.query\
                .join(proxy_group)\
                .filter(proxy_group.api_key == get_x_api_key())\
                .filter(hotspot.address == hotspot_address).first()

        if has_correct_api_key:
            return handler_function(*args, **kwargs)
        
        return {'message' : 'invalid api key'}, 401
    
    return decorator
