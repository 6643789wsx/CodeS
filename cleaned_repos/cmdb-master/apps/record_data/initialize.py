from django.conf import settings
from elasticsearch.exceptions import NotFoundError, TransportError
from rest_framework import exceptions, mixins, permissions, serializers, viewsets
from rest_framework.response import Response
from utils.es import es

from . import views


def add_viewset(table):
    data_index = table.name
    record_data_index = "{}.".format(table.name)
    deleted_data_index = "{}..".format(table.name)

    def retrieve(self, request, *args, **kwargs):
        try:
            res = es.search(
                index=record_data_index,
                doc_type="record-data",
                body={"query": {"term": {"S-data-id": kwargs["pk"]}}},
                sort="S-update-time:desc",
            )
        except NotFoundError as exc:
            raise exceptions.NotFound(
                "Document {} was not found in Type data of Index {}".format(
                    kwargs["pk"], record_data_index
                )
            )
        except TransportError as exc:
            return Response([])
        return Response(res["hits"])

    viewset = type(
        table.name,
        (mixins.RetrieveModelMixin, viewsets.GenericViewSet),
        dict(permission_classes=(permissions.IsAuthenticated,), retrieve=retrieve),
    )
    setattr(views, table.name, viewset)
    return viewset
