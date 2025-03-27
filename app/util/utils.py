import unicodedata


def remove_accents_and_spaces(s):
    nfkd_form = unicodedata.normalize('NFKD', s)
    no_acento = ''.join([c for c in nfkd_form if not unicodedata.combining(c)])
    return no_acento.replace(" ", "_")


def to_camel_case(snake_str):
    cleaned_str = remove_accents_and_spaces(snake_str)

    components = cleaned_str.split('_')
    return components[0].lower() + ''.join(x.title() for x in components[1:])


def convert_dict_keys_to_camel_case(data):
    if isinstance(data, dict):
        return {to_camel_case(key): convert_dict_keys_to_camel_case(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [convert_dict_keys_to_camel_case(item) for item in data]
    return data
