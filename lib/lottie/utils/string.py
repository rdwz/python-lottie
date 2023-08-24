import re

def camel_to_snake_helper(text):
    return re.sub("([a-z])([A-Z])", r"\1_\2", text)


def camel_to_caps(text):
    return camel_to_snake_helper(text).upper()


def camel_to_snake(text):
    return camel_to_snake_helper(text).lower()


def snake_to_camel(text):
    return "".join(s.title() for s in text.split("_"))
