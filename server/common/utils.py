import re
import json
from django.conf import settings
import boto3


def get_mturk_client():
    endpoint_url = settings.MTURK_ENDPOINT_URL
    client = boto3.client('mturk', endpoint_url=endpoint_url)
    return client


PARSE_REGEX = re.compile(r"<FreeText>(.*)</FreeText>", re.MULTILINE)

def parse_answer_xml(answer_xml):
    answer_text = PARSE_REGEX.search(answer_xml).group(1)
    answer = json.loads(answer_text)
    return answer


# def build_field_to_param_fns(field_param_mappings):
#     """
#     Build a dict of functions, indexed by field names, that map field values to request parameters.
#     """
#     fns = {}
#     for mapping in field_param_mappings:
#         if len(mapping) == 2: # direct copy
#             field_name, param_name = mapping
#             fns[field_name] = lambda f: f
#         elif len(mapping) == 4:
#             field_name, param_name, f2p_fn, _ = mapping
#             fns[field_name] = lambda f: f2p_fn(f)
#         else:
#             raise ValueError('Mappings must be 2- or 4-tuples.')

#     return fns


# def build_param_to_field_fns(field_param_mappings):
#     """
#     Build a dict of functions, indexed by field names, that map response values to field values.
#     """
#     fns = {}
#     for mapping in field_param_mappings:
#         if len(mapping) == 2: # direct copy
#             field_name, param_name = mapping
#             fns[field_name] = lambda r: r
#         elif len(mapping) == 4:
#             field_name, param_name, _, p2f_fn = mapping
#             fns[field_name] = lambda r: p2f_fn(r)
#         else:
#             raise ValueError('Mappings must be 2- or 4-tuples.')


def _find_mapping_by_field_name(field_name, mappings):
    mapping = [m for m in mappings if m[0] == field_name]
    if len(mapping) == 0:
        raise ValueError('Field name {} not found in mappings'.format(field_name))
    elif len(mapping) > 1:
        raise valueError('Invalid mappings: Multiple field name {} found.'.format(field_name))
    return mapping[0]


def _find_mapping_by_param_key(param_key, mappings):
    mapping = [m for m in mappings if m[1] == param_key]
    if len(mapping) == 0:
        raise ValueError('Param key {} not found in mappings'.format(param_key))
    elif len(mapping) > 1:
        raise valueError('Invalid mappings: Multiple param key {} found.'.format(param_key))
    return mapping[0]


def set_fields_from_params(obj, params, mappings, field_names):
    """Set field values from a dict of parameters, which is the response from MTurk
        Args
            obj: The object to set fields
            params: A dict of parameters. It should be the response from MTurk
            mappings: a list/tuple of 2- or 4-tuples describing name mappings of fields and params,
                      with optional value mapping functions in both directions
            field_names: Fields to set
    """
    for field_name in field_names:
        if not hasattr(obj, field_name):
            raise ValueError('Object {} has no field named {}'.format(obj, field_name))
        
        mapping = _find_mapping_by_field_name(field_name, mappings)
        
        if len(mapping) == 2: # direct copy
            field_name, param_key = mapping
            setattr(obj, field_name, params[param_key])
        elif len(mapping) == 4: # mapping functions
            field_name, param_key, _, p2f_fn = mapping
            field_value = p2f_fn(params[param_key])
            setattr(obj, field_name, field_value)
        else:
            raise ValueError('Mappings must be 2- or 4-tuples.')


def get_params_from_fields(obj, mappings, field_names, skip_none=True):
    """Get a dict of parameters used in the request to MTurk
        Args
            obj: The object to set fields
            mappings: a list/tuple of 2- or 4-tuples describing name mappings of fields and params,
                      with optional value mapping functions in both directions
            field_names: Fields to get
            skip_none: skip fields that have None values
    """
    params = {}
    for field_name in field_names:
        if not hasattr(obj, field_name):
            raise ValueError('Object {} has no field named {}'.format(obj, field_name))

        field_value = getattr(obj, field_name)
        if skip_none and field_value is None:
            continue

        mapping = _find_mapping_by_field_name(field_name, mappings)
        if len(mapping) == 2: # direct copy
            field_name, param_key = mapping
            params[param_key] = field_value
        elif len(mapping) == 4: # mapping functions
            field_name, param_key, f2p_fn, _ = mapping
            params[param_key] = f2p_fn(field_value)
        else:
            raise ValueError('Mappings must be 2- or 4-tuples.')
    return params


# Django field validators
def validate_list_of_integer(value):
    if not isinstance(value, list):
        raise ValidationError('Input value should be a list of integers')
    for v in value:
        if not isinstance(value, int):
            raise ValidationError('Input value should be a list of integers')


def polygon_iou(poly1, poly2):
    raise NotImplementedError('')


def polygon_center(polygon):
    avg = lambda l: sum(l) / len(l)
    center_x = avg([p['x'] for p in polygon])
    center_y = avg([p['y'] for p in polygon])
    return {'x': center_x, 'y': center_y}
