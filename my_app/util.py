import functools
import operator

from django.db.models import Q
from django.utils import timezone
from django.utils.encoding import smart_str

from input.models import Item
from my_app.models import BomModel


class BomNr(object):
    @staticmethod
    def get_nr():
        data = Item.objects.all().values("id", "nr")
        item_data = {}
        for i in data:
            item_data[i["id"]] = i["nr"]
        return item_data


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


class BomData(object):
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
            bom_query = obj.objects.all().filter(functools.reduce(operator.iand, q_filters))
        else:
            bom_query = obj.objects.all().filter(effective_end__gte=current_time).order_by("id")
        # 根据查询的列表拼接URL
        array = []
        for i in fs:
            for k, v in i.items():
                b = "&" + str(k) + "=" + str(v)
                array.append(b)
        query_url = "".join(array)

        def get_deep_tree(parents):

            display_tree = []
            # 所有父节点
            for p in parents:
                node = TreeNode()
                node.id = p.id
                node.text = p.item.nr
                node.tags = [p.id]
                node.query_url = query_url
                children = BomModel.objects.filter(parent_id=p.id)
                if len(children) > 0:
                    node.nodes = get_deep_tree(children)
                display_tree.append(node.to_dict())
            return display_tree

        bom_root = bom_query.filter(parent=None)
        if bom_root:
            node_data = get_deep_tree(bom_root)
        else:
            node_data = get_deep_tree(bom_query)

        return bom_query, node_data, fs, query_url, search


class TreeNode(object):
    def __init__(self):
        self.id = 0
        self.text = "Node 1"
        self.nodes = []
        self.tags = []
        self.query_url = ""
        self.href = ""

    def to_dict(self):
        return {
            'id': self.id,
            'text': self.text,
            'nodes': self.nodes,
            'tags': self.tags,
            "href": "?page=1&id=%s%s" % (self.id, self.query_url)
        }