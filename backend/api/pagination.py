from rest_framework.pagination import PageNumberPagination
# from rest_framework. response import Response
# from rest_framework.utils.urls import remove_query_param, replace_query_param


class CustomPagination(PageNumberPagination):

    page_size_query_param = 'limit'

    # def get_paginated_response(self, data):
    #     return Response(
    #         {
    #             'next': self.get_next_link(),
    #             'previous': self.get_previous_link(),
    #             'count': self.page.paginator.count,
    #             'results': data,
    #         }
    #     )

    # def get_next_link(self):
    #     if not self.page.has_next():
    #         return None
    #     url = self.request.get_full_path()
    #     page_number = self.page.next_page_number()
    #     return replace_query_param(url, self.page_query_param, page_number)

    # def get_previous_link(self):
    #     if not self.page.has_previous():
    #         return None
    #     url = self.request.get_full_path()
    #     page_number = self.page.previous_page_number()
    #     if page_number == 1:
    #         return remove_query_param(url, self.page_query_param)
    #     return replace_query_param(url, self.page_query_param, page_number)
