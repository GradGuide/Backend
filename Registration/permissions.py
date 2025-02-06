# permissions.py
from rest_framework import permissions

class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    Admins can edit any object.
    """

    def has_object_permission(self, request, view, obj):
        return obj == request.user or request.user.is_admin
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import permission_classes

@permission_classes([IsAuthenticated])
class ProtectedView(APIView):
    def get(self, request):
        return Response({"message": "This is a protected endpoint."})
