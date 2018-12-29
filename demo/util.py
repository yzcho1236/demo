import math
import operator
from functools import wraps
import functools
import six
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.utils import timezone
from django.http import HttpResponseRedirect
from django.utils.encoding import smart_str
from input.models import Item, Tree_Model


def perm_required(perm, raise_exception=False):
    def check_perms(user):
        if isinstance(perm, six.string_types):
            perms = (perm,)
        else:
            perms = perm
        if user.has_perms(perms):
            return True
        if raise_exception:
            return PermissionDenied
        return False

    return passes_test(check_perms)


def passes_test(test_func):
    def decorator(view_func):
        # 获取当前请求的对象
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if test_func(request.user):
                return view_func(request, *args, **kwargs)
            return HttpResponseRedirect("/index/?msg=用户没有访问的权限")

        return _wrapped_view

    return decorator


class Pagination(object):
    def __init__(self, queryset, pagesize=20, page=1):
        self.pagesize = 20
        self.queryset = queryset
        self.count = float(self.queryset.count())
        self.total_pages = int(math.ceil(self.count / self.pagesize))
        self.page = page
        if self.page:
            self.page = int(self.page)
        if self.page > self.total_pages:
            self.page = self.total_pages
        if self.page < 1:
            self.page = 1

        self.prev = 1 if self.page == 1 else self.page - 1
        self.next = self.page if self.page == self.total_pages else self.page + 1

    def get_objs(self):
        cnt = (self.page - 1) * self.pagesize
        objs = self.queryset[cnt: cnt + self.pagesize]
        return objs


class GetItemParent(object):
    @staticmethod
    def get_parent():
        items = Item.objects.all().order_by("id").values("id", "nr")
        item_all = {}
        for i in items:
            item_all[i["id"]] = i["nr"]
        return item_all


class GetBom(object):
    @staticmethod
    def get_bom(id, name):
        alist_id = [id]
        alist_name = [name]
        item = Tree_Model.objects.get(id=id)
        for i in item.get_children():
            alist_id.append(i.id)
            alist_name.append(i.name)
        for i in item.get_ancestors():
            alist_id.append(i.id)
            alist_name.append(i.name)
        boms = Tree_Model.objects.all().exclude(Q(name__in=alist_name) | Q(id__in=alist_id)).values_list("name",
                                                                                                         flat=True).\
            order_by("name").distinct("name")
        return boms


_filter_map_jqgrid_django = {
    'ne': ('%(field)s__iexact', True),
    'bn': ('%(field)s__istartswith', True),
    'en': ('%(field)s__iendswith', True),
    'nc': ('%(field)s__icontains', True),
    'ni': ('%(field)s__in', True),
    'in': ('%(field)s__in', False),
    'eq': ('%(field)s__iexact', False),
    'bw': ('%(field)s__istartswith', False),
    'gt': ('%(field)s__gt', False),
    'ge': ('%(field)s__gte', False),
    'lt': ('%(field)s__lt', False),
    'le': ('%(field)s__lte', False),
    'ew': ('%(field)s__iendswith', False),
    'cn': ('%(field)s__icontains', False)
}
_filter_map_jqgrid_django_mptt = {
    'ne': ('%(field)s__exact', True),
    'bn': ('%(field)s__startswith', True),
    'en': ('%(field)s__endswith', True),
    'nc': ('%(field)s__contains', True),
    'ni': ('%(field)s__in', True),
    'in': ('%(field)s__in', False),
    'eq': ('%(field)s__exact', False),
    'bw': ('%(field)s__startswith', False),
    'gt': ('%(field)s__gt', False),
    'ge': ('%(field)s__gte', False),
    'lt': ('%(field)s__lt', False),
    'le': ('%(field)s__lte', False),
    'ew': ('%(field)s__endswith', False),
    'cn': ('%(field)s__contains', False)
}

select_op = {'eq': '等于', 'ne': '不等于', 'lt': '小于', 'le': '小于等于', 'gt': '大于等于', 'bw': '开始于', 'bn': '不开始于', 'in': '属于',
             'ni': '不属于', 'cn': '包含', 'nc': '不包含'}


class GetQueryData(object):
    @staticmethod
    def get_data(obj, query_data, filter_fields):
        # 查询的条件
        q_filters = []
        fs = []
        if "data" in query_data and "op" in query_data and "data" in query_data:
            data_query = list(filter(lambda x: x, query_data["data"]))
            len_data_query = len(data_query)
            fields = query_data["field"]
            ops = query_data["op"]
            # 查询的有效列表
            # 查询的所有列表
            for i in range(0, len_data_query):
                adict = {}
                if fields[i] in filter_fields:
                    adict["field"] = fields[i]
                    adict["op"] = ops[i]
                    adict["data"] = data_query[i]
                    fs.append(adict)
                else:
                    continue

            for rule in fs:
                op, field, data = rule['op'], rule['field'], rule['data']
                filter_fmt, exclude = _filter_map_jqgrid_django[op]
                filter_str = smart_str(filter_fmt % {'field': field})

                if filter_fmt.endswith('__in'):
                    filter_kwargs = {filter_str: data.split(',')}
                else:
                    filter_kwargs = {filter_str: smart_str(data)}

                if exclude:
                    q_filters.append(~Q(**filter_kwargs))
                else:
                    q_filters.append(Q(**filter_kwargs))

        if q_filters:
            item_query = obj.objects.filter(functools.reduce(operator.iand, q_filters)).order_by("id")
        else:
            item_query = obj.objects.all()
        # 根据查询的列表拼接URL
        array = []
        for i in fs:
            for k, v in i.items():
                b = "&" + str(k) + "=" + str(v)
                array.append(b)
        query_url = "".join(array)

        return item_query, fs, query_url

    @staticmethod
    def get_tree(obj, query_data, filter_fields):
        # 查询的条件
        q_filters = []
        alist = []
        fs = []
        search = False
        current_time = timezone.now()
        if "data" in query_data and "op" in query_data and "data" in query_data:
            search = True
            data_query = query_data["data"]
            data_len = len(data_query)

            fields = query_data["field"]
            ops = query_data["op"]

            # 这里出错了
            for i in range(data_len):
                adict = {}
                if fields[i] in filter_fields:
                    adict["field"] = fields[i]
                    adict["op"] = ops[i]
                    adict["data"] = query_data["data"][i]
                    alist.append(adict)
                else:
                    continue

            # 将有效的查询条件放到fs中
            for i in range(len(alist)):
                if alist[i]["data"]:
                    fs.append(alist[i])

            for rule in fs:
                op, field, data = rule['op'], rule['field'], rule['data']
                filter_fmt, exclude = _filter_map_jqgrid_django_mptt[op]
                filter_str = smart_str(filter_fmt % {'field': field})

                if filter_fmt.endswith('__in'):
                    filter_kwargs = {filter_str: data.split(',')}
                else:
                    filter_kwargs = {filter_str: smart_str(data)}

                if exclude:
                    q_filters.append(~Q(**filter_kwargs))
                else:
                    q_filters.append(Q(**filter_kwargs))

        if q_filters:
            item_query = obj._tree_manager.filter(functools.reduce(operator.iand, q_filters))
        else:
            item_query = obj.objects.all().filter(effective_end__gte=current_time)
        # 根据查询的列表拼接URL
        array = []
        for i in fs:
            for k, v in i.items():
                b = "&" + str(k) + "=" + str(v)
                array.append(b)
        query_url = "".join(array)

        return item_query, fs, query_url, search
