from rest_framework.permissions import BasePermission


class HasOrganization(BasePermission):
    message = "User must belong to an organization."

    def has_permission(self, request, view) -> bool:
        return bool(request.user and request.user.is_authenticated and request.user.organization_id)


class IsAnalystOrAdmin(BasePermission):
    message = "Analyst or admin role required."

    def has_permission(self, request, view) -> bool:
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role in {"analyst", "admin"}
        )
