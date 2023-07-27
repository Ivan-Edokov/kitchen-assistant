from rest_framework import permissions


class RegisterProfileOrAutorised(permissions.BasePermission):
    """Разрешение для пользовательского набора представлений.
    Разрешает Регистрацию нового пользователя
    и доступ к /users/{id} для неавторизованных.
    Отключить ДОСТУП к /users/me/ для неавторизованных.
    Разрешить ПУБЛИКАЦИЮ и УДАЛЕНИЕ в /subscribe/ для авторизованных.
    """

    def has_permission(self, request, view):
        path_end = request.path_info.split('/')[-2]
        auth_allow_method = ('GET', 'POST')
        return (
            (
                (
                    request.method in auth_allow_method
                    or (
                        view.action == 'subscribe'
                        and request.method == 'DELETE'
                    )
                )
                and request.user.is_authenticated
                and view.action != 'create'
            )
            or (view.action == 'create' and not request.user.is_authenticated)
            or (view.action == 'retrieve' and path_end != 'me')
        )


class OnlyGet(permissions.BasePermission):
    """Разрешение только для чтения."""

    def has_permission(self, request, viev):
        return request.method == 'GET'


class OnlyGetAutorised(permissions.BasePermission):
    """Разрешения для чтения авторизованных"""

    def has_permission(self, request, view):
        return request.method == 'GET' and request.user.is_authenticated
