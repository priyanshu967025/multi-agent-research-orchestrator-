from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Object-level permission: only the owner of a ResearchSession may mutate it.
    
    Assumes the model instance has a ``user`` ForeignKey. Read-only access
    (GET, HEAD, OPTIONS) is allowed for anyone; write access (PUT, PATCH,
    DELETE) requires ``obj.user == request.user``.
    """

    def has_object_permission(self, request, view, obj):
        # Safe methods are always permitted.
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user


class IsSessionOwner(permissions.BasePermission):
    """View-level permission: only authenticated users may access."""

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
