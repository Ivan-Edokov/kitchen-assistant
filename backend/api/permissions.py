from rest_framework import permissions


class PostOrAutorised(permissions.BasePermission):
    """Метод Пост или запрос от авторизованного"""

    def has_permission(self, request, view):
        return request == 'Post' or request.user.is_authenticated
