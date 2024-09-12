from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def is_excludable(status, creator_status):
    return status != "admin" and creator_status
