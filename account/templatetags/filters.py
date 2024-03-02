from django import template


register = template.Library()


@register.filter
def add_class(field, class_name):
    return field.as_widget(attrs={
        "class": " ".join((field.css_classes(), class_name))
    })


@register.filter
def add_placeholder(value, placeholder):
    value.field.widget.attrs["placeholder"] = placeholder
    return value


@register.filter
def dir(value, dir):
    value.field.widget.attrs["dir"] = dir
    return value
