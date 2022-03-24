from functools import wraps
from typing import Callable, Type
from flask import make_response, request

from pydantic import BaseModel, ValidationError


def pydantic_params(query_params_model: Type[BaseModel], source_attr: str = 'values') -> Callable:
    def _decorator(func: Callable) -> Callable:

        @wraps(func)
        def _wrapper(*args, **kwargs):
            data = getattr(request, source_attr)
            if data is None:
                return make_response({
                    'errors': {'error': 'data is empty'}
                }, 400)
            
            try:
                params = query_params_model(**data)
            except TypeError as err:
                return make_response({
                    'errors': {'error': 'data is empty'}
                }, 400)
            except ValidationError as err:
                return make_response(
                    {
                        'errors': {
                            'params': {e['loc'][0]: str(e['msg']) for e in err.errors()}
                        }
                    },
                    400
                )
            
            return func(params, *args, **kwargs)

        return _wrapper
    return _decorator
