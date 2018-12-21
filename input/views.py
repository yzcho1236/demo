import urllib
from datetime import datetime
from io import BytesIO

from django.db import transaction
from django.http import HttpResponse, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.utils.encoding import force_str
from django.views import View
from openpyxl import Workbook
from openpyxl.cell import WriteOnlyCell

from demo.util import Pagination, GetItemParent, GetBom, GetQueryData, select_op
from input.form import BomForm
from input.models import Tree_Model


class Bom(View):
    file_headers = ('id', '物料', '组成物料', '生效开始', "生效结束", "数量")
    select_field = {"id": "id", 'parent__nr': '物料', 'nr': '组成物料', 'effective_start': '生效开始', 'effective_end': '生效结束'}

    def get(self, request, *args, **kwargs):
        fmt = request.GET.get('format', None)
        if fmt is None:
            content = self._get_data(request)
            return TemplateResponse(request, "bom.html", content)
        elif fmt == 'spreadsheet':
            # 下载 excel
            json = self._get_data(request, in_page=False)

            wb = Workbook(write_only=True)
            title = "物料清单"
            ws = wb.create_sheet(title)

            headers = []
            for h in self.file_headers:
                cell = WriteOnlyCell(ws, value=h)
                headers.append(cell)
            ws.append(headers)

            body_fields = ("id", "parent", "child", "effective_start", "effective_end", "qty")
            data = []
            for i in json["nodes"]:
                adict = {}
                adict["id"] = i.id
                adict["child"] = i.nr
                if i.parent:
                    adict["parent"] = i.parent.nr
                else:
                    adict["parent"] = i.nr
                adict["effective_start"] = i.effective_start
                adict["effective_end"] = i.effective_end
                adict["qty"] = i.qty
                data.append(adict)

            for i in data:
                body = []
                for field in body_fields:
                    if field in i:
                        cell = WriteOnlyCell(ws, value=i[field])
                        body.append(cell)
                ws.append(body)
            output = BytesIO()
            wb.save(output)
            response = HttpResponse(
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                content=output.getvalue()
            )
            response['Content-Disposition'] = "attachment; filename*=utf-8''%s.xlsx" % urllib.parse.quote(
                force_str(title))
            response['Cache-Control'] = "no-cache, no-store"
            return response

    def _get_data(self, request, in_page=True, *args, **kwargs):

        # 获取到的页面数
        page = request.GET.get("page", 1)
        query_data = dict(request.GET.lists())
        item_query, fs, query_url, search = GetQueryData.get_tree(Tree_Model, query_data, self.select_field)
        if search:
            request.session["bom_query_url"] = query_url
        count = float(item_query.count())
        pagesize = 10 if in_page else count
        pagination = Pagination(item_query, pagesize, page)

        item_id = request.GET.get("id", None)
        page = request.GET.get("page", 1)
        data = []
        if item_id:
            id = item_id
        else:
            id = item_query.first().id
        item = Tree_Model.objects.get(id=id)
        pagination = Pagination(item_query, request.pagesizes, page)
        child = Tree_Model.objects._mptt_filter(parent__id=id)
        for i in child:
            adict = {}
            adict["id"] = i.id
            adict["child"] = i.nr
            adict["parent"] = item.nr
            adict["effective_start"] = i.effective_start
            adict["effective_end"] = i.effective_end
            adict["qty"] = i.qty
            data.append(adict)

        content = {
            "id": id,
            "item": item.nr,
            "pg": pagination,
            "nodes": pagination.get_objs(),
            "data": data,
            "query": fs,
            "query_url": request.session.get("bom_query_url", None) if request.session.get("bom_query_url",
                                                                                           None) else "",
            "select_op": select_op,
            "select_field": self.select_field,
            "perm": request.perm
        }
        return content


class BomAdd(View):
    def get(self, request, *args, **kwargs):
        content = {"item": GetBom.get_bom(), "child": GetBom.get_bom(), "perm": request.perm}
        return TemplateResponse(request, "bom_add.html", content)

    def post(self, request, *args, **kwargs):
        form = BomForm(request.POST)
        form_get = request.POST.dict()
        item_select = int(form_get["item"])
        child_select = int(form_get["child"])
        # 生效开始和生效结束可能为空
        effective_start = form_get["effective_start"] if form_get["effective_start"] else datetime(datetime.now().year,
                                                                                                   datetime.now().month,
                                                                                                   datetime.now().day)
        effective_end = form_get["effective_end"] if form_get["effective_end"] else datetime(2030, 12, 31)
        qty = form_get["qty"]
        content = {
            "item_select": item_select,
            "child_select": child_select,
            "item": GetBom.get_bom(),
            "child": GetBom.get_bom(),
            "effective_start": effective_start,
            "effective_end": effective_end,
            "qty": qty,
            "error": ""
        }
        if form.is_valid():
            with transaction.atomic(savepoint=False):
                try:
                    bom_add = Tree_Model.objects.get(id=child_select)
                    item = Tree_Model.objects.get(id=item_select)
                    bom_add.effective_start = effective_start
                    bom_add.effective_end = effective_end
                    bom_add.qty = qty
                    bom_add.save()
                    bom_add.move_to(item)

                except Exception as e:
                    print(e)
                    content["error"] = e
                    return TemplateResponse(request, "bom_add.html", content)
                else:
                    return HttpResponseRedirect("/bom/")
        else:
            content["error"] = "表单错误"
            return TemplateResponse(request, "bom_add.html", content)


class BomCalculate(View):
    pass
