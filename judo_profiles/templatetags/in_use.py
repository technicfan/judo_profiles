from django import template
from django.contrib.admin.utils import NestedObjects
from django.db import DEFAULT_DB_ALIAS

register = template.Library()


@register.filter
def in_use(obj):
    collector = NestedObjects(using=DEFAULT_DB_ALIAS)
    collector.collect([obj])
    return len(collector.nested()) > 1
