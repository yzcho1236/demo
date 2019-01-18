from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CustomerNumberPagination(PageNumberPagination):
    # 每页显示多少个
    page_size = 1
    # 默认每页显示3个，可以通过传入pager1/?page=2&size=4,改变默认每页显示的个数
    page_size_query_param = "pagesize"
    # 获取页码数的
    page_query_param = "page"

    #自定义分页返回
    def get_paginated_response(self, data):
        return Response({
        # 当前页
        'page': self.page.number,
        # 每页个数
        'pagesize': self.page.paginator.per_page,
        # 总个数
        'count': self.page.paginator.count,
        # 总页数
        'total_pages': self.page.paginator.num_pages,
        # 数据
        'results': data
        })