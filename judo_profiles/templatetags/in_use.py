from django import template
from django.db.models.deletion import Collector

register = template.Library()


@register.filter
def in_use(obj):
    collector = Collector(using="default")
    collector.collect([obj])
    return not all([not i for i in collector.fast_deletes])
