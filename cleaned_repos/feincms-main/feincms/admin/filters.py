from django.contrib.admin.filters import ChoicesFieldListFilter
from django.db.models import Count
from django.utils.encoding import smart_str
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from feincms.utils import shorten_string


class ParentFieldListFilter(ChoicesFieldListFilter):
    """
    Improved list_filter display for parent Pages by nicely indenting hierarchy

    In theory this would work with any mptt model which uses a "title"
    attribute.

    my_model_field.page_parent_filter = True
    """

    def __init__(self, f, request, params, model, model_admin, field_path=None):
        super().__init__(f, request, params, model, model_admin, field_path)

        parent_ids = (
            model.objects.exclude(parent=None)
            .values_list("parent__id", flat=True)
            .order_by("parent__id")
            .distinct()
        )
        parents = model.objects.filter(pk__in=parent_ids).values_list(
            "pk", "title", "level"
        )
        self.lookup_choices = [
            (
                pk,
                "{}{}".format(
                    "&nbsp;&nbsp;" * level, shorten_string(title, max_length=25)
                ),
            )
            for pk, title, level in parents
        ]

    def choices(self, cl):
        yield {
            "selected": self.lookup_val is None,
            "query_string": cl.get_query_string({}, [self.lookup_kwarg]),
            "display": _("All"),
        }

        for pk, title in self.lookup_choices:
            yield {
                "selected": pk == int(self.lookup_val or "0"),
                "query_string": cl.get_query_string({self.lookup_kwarg: pk}),
                "display": mark_safe(smart_str(title)),
            }

    def title(self):
        return _("Parent")


class CategoryFieldListFilter(ChoicesFieldListFilter):
    """
    Customization of ChoicesFilterSpec which sorts in the user-expected format

    my_model_field.category_filter = True
    """

    def __init__(self, f, request, params, model, model_admin, field_path=None):
        super().__init__(f, request, params, model, model_admin, field_path)

        # Restrict results to categories which are actually in use:
        related_model = f.remote_field.model
        related_name = f.related_query_name()

        self.lookup_choices = sorted(
            (
                (i.pk, f"{i} ({i._related_count})")
                for i in related_model.objects.annotate(
                    _related_count=Count(related_name)
                ).exclude(_related_count=0)
            ),
            key=lambda i: i[1],
        )

    def choices(self, cl):
        yield {
            "selected": self.lookup_val is None,
            "query_string": cl.get_query_string({}, [self.lookup_kwarg]),
            "display": _("All"),
        }

        for pk, title in self.lookup_choices:
            yield {
                "selected": pk == int(self.lookup_val or "0"),
                "query_string": cl.get_query_string({self.lookup_kwarg: pk}),
                "display": mark_safe(smart_str(title)),
            }

    def title(self):
        return _("Category")
