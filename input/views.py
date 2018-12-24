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
from input.form import BomForm, BomEditForm
from input.models import Tree_Model


class Bom(View):
    file_headers = ('id', '物料', '组成物料', '生效开始', "生效结束", "数量")
    select_field = {"id": "id", 'parent__name': '物料', 'name': '组成物料', 'effective_start': '生效开始',
                    'effective_end': '生效结束'}

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
                adict["child"] = i.name
                if i.parent:
                    adict["parent"] = i.parent.name
                else:
                    adict["parent"] = i.name
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

    def post(self, request, *args, **kwargs):
        """上传Excel"""
        if request.FILES and len(request.FILES) == 1:
            count = 0
            for filename, file in request.FILES.items():
                if file.content_type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
                    count += 1
            if count == 0:
                data = self._get_data(request)
                data["error"] = "请选择Excel文件进行上传"
                return TemplateResponse(request, "item.html", data)



        else:
            data = self._get_data(request)
            data["error"] = "没有上传文件"
            return TemplateResponse(request, "item.html", data)

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
        parent = Tree_Model.objects.get(id=id)
        pagination = Pagination(item_query, request.pagesizes, page)
        items = Tree_Model.objects._mptt_filter(parent__id=id)
        for i in items:
            adict = {}
            adict["id"] = i.id
            adict["child"] = i.name
            adict["parent"] = parent.name
            adict["effective_start"] = i.effective_start
            adict["effective_end"] = i.effective_end
            adict["qty"] = i.qty
            data.append(adict)

        content = {
            "id": id,
            "parent": parent.name,
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
        parent = request.GET.get("name", None)
        parent_id = request.GET.get("id", None)
        items = GetBom.get_bom(parent_id, parent)
        content = {
            "parent_id": parent_id,
            "parent": parent,
            "items": items,
            "perm": request.perm
        }
        return TemplateResponse(request, "bom_add.html", content)

    def post(self, request, *args, **kwargs):
        form = BomForm(request.POST)
        form_get = request.POST.dict()
        parent_id = form_get["parent_id"]
        parent = form_get["parent"]
        item = form_get["item"]
        # 生效开始和生效结束可能为空
        effective_start = form_get["effective_start"] if form_get["effective_start"] else datetime(datetime.now().year,
                                                                                                   datetime.now().month,
                                                                                                   datetime.now().day)
        effective_end = form_get["effective_end"] if form_get["effective_end"] else datetime(2030, 12, 31)
        qty = form_get["qty"]
        content = {
            "parent_id": parent_id,
            "parent": parent,
            "items": GetBom.get_bom(parent_id, parent),
            "item": item,
            "effective_start": effective_start,
            "effective_end": effective_end,
            "qty": qty,
            "error": ""
        }
        if form.is_valid():
            with transaction.atomic(savepoint=False):
                try:
                    Tree_Model.objects.filter(parent__name=item).first()
                    Tree_Model.objects.create(name=item, parent_id=parent_id, effective_start=effective_start,
                                              effective_end=effective_end, qty=qty)



                except Exception as e:
                    print(e)
                    content["error"] = e
                    return TemplateResponse(request, "bom_add.html", content)
                else:
                    return HttpResponseRedirect("/bom/")
        else:
            content["error"] = "表单错误"
            return TemplateResponse(request, "bom_add.html", content)


class BomEdit(View):
    def get(self, request, *args, **kwargs):
        id = request.GET.get("id", None)
        if id:
            item = Tree_Model.objects.get(id=id)
            content = {
                "id": id,
                "name": item.name,
                "effective_start": datetime.strftime(item.effective_start, "%Y-%m-%d"),
                "effective_end": datetime.strftime(item.effective_end, "%Y-%m-%d"),
                "qty": item.qty,
                "perm": request.perm
            }
            return TemplateResponse(request, "bom_edit.html", content)
        else:
            return HttpResponseRedirect("/bom/?mag=查询数据失败")

    def post(self, request, *args, **kwargs):
        form = BomEditForm(request.POST)
        # 获取表单数据
        id = request.POST['id']
        name = request.POST['name']
        start = request.POST["effective_start"]
        effective_start = request.POST["effective_start"] if request.POST["effective_start"] else datetime(
            datetime.now().year,
            datetime.now().month,
            datetime.now().day)
        effective_end = request.POST["effective_end"] if request.POST["effective_end"] else datetime(2030, 12, 31)
        qty = request.POST['qty']
        content = {
            "id": id,
            "name": name,
            "effective_start": effective_start,
            "effective_end": effective_end,
            "qty": qty,
            "perm": request.perm
        }
        if form.is_valid():

            with transaction.atomic(savepoint=False):
                # 创建保存点
                try:
                    item = Tree_Model.objects.get(id=id)
                    item.name = name
                    item.effective_start = effective_start
                    item.effective_end = effective_end
                    item.qty = qty
                    item.save()
                except Exception as e:
                    print(e)
                    content["error"] = "编辑失效"
                    return TemplateResponse(request, "bom_edit.html", content)
                else:
                    return HttpResponseRedirect("/bom/")
        else:
            content["error"] = "表单填写错误"
            return TemplateResponse(request, "bom_edit.html", content)


class BomCalculate(View):
    def get(self, request, *args, **kwargs):
        fmt = request.GET.get('format', None)
        if fmt is None:
            content = self._get_data(request)
            return TemplateResponse(request, "bom_calculate.html", content)
        else:
            # 下载Excel
            data = self._get_data(request)
            print(data)
            wb = Workbook()
            title = "bom计算"
            # ws1 = wb.worksheets[0]
            # ws1.title = "采购物料"
            # ws2 = wb.worksheets[1]
            # ws2.title = "制造物料"
            ws1 = wb.create_sheet("采购物料", 0)
            ws2 = wb.create_sheet("制造物料", 1)

            header1 = []
            header2 = []

            purchase_headers = ("采购物料", "数量")
            manufacture_headers = ("制造物料", "数量")
            for h in purchase_headers:
                cell = WriteOnlyCell(ws1, value=h)
                header1.append(cell)
            ws1.append(header1)
            body_fields = ("name", "qty")
            for i in data['purchase']:
                body = []
                for field in body_fields:
                    if field in i:
                        cell = WriteOnlyCell(ws1, value=i[field])
                        body.append(cell)
                ws1.append(body)

            for h in manufacture_headers:
                cell = WriteOnlyCell(ws2, value=h)
                header2.append(cell)
            ws2.append(header2)
            for i in data['purchase']:
                body = []
                for field in body_fields:
                    if field in i:
                        cell = WriteOnlyCell(ws2, value=i[field])
                        body.append(cell)
                ws2.append(body)

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

    def _get_data(self, request, *args, **kwargs):
        id = request.GET.get("id", None)
        number = int(request.GET.get("qty", None))
        item = Tree_Model.objects.get(id=id)
        # 计算采购物料的qty
        purchase_list = []
        manufacture_list = []
        purchase = item.get_leafnodes()
        child = item.get_descendants()
        if list(purchase) == list(child):
            for i in purchase:
                adict = {}
                adict["qty"] = i.qty * number
                adict["name"] = i.name
                purchase_list.append(adict)

        else:

            # manufacture = manufacture[:-len(purchase)]
            # 制造物料的qty
            for i in child:
                adict = {}
                adict["qty"] = i.qty * number
                adict["name"] = i.name
                manufacture_list.append(adict)

            for i in purchase:
                adict = {}
                adict["qty"] = i.qty * number
                adict["name"] = i.name
                purchase_list.append(adict)

        def getQty(child):
            for i in child:
                i.get_children()

        content = {
            "id": id,
            "item": item.name,
            "qty": number,
            "purchase": purchase_list,
            "manufacture": manufacture_list
        }
        return content
