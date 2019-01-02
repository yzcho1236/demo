import traceback
import urllib
from datetime import datetime
from io import BytesIO

from django.db import transaction
from django.http import HttpResponse, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.utils import timezone
from django.utils.encoding import force_str
from django.views import View
from openpyxl import Workbook
from openpyxl.cell import WriteOnlyCell

from demo.util import Pagination, select_op
from input.form import BomEditForm
from input.models import Tree_Model
from my_app.form import ItemBomForm
from my_app.models import BomModel
from my_app.util import BomNr, BomData


class ItemBom(View):
    select_field = {"id": "id", 'parent__nr': '物料', 'nr': '组成物料代码', 'effective_start': '生效开始', 'effective_end': '生效结束'}

    def get(self, request, *args, **kwargs):
        content = self._get_data(request)
        return TemplateResponse(request, "my_app_template/bom.html", content)

    def _get_data(self, request, in_page=True, *args, **kwargs):
        page = request.GET.get("page", 1)
        query_data = dict(request.GET.lists())
        bom_query, node_data, fs, query_url, search = BomData.get_tree(BomModel, query_data, self.select_field)
        if search:
            request.session["bom_query_url"] = query_url
        count = float(bom_query.count())
        pagesize = request.pagesizes if in_page else count
        pagination = Pagination(bom_query, pagesize, page)

        item_id = request.GET.get("id", None)
        page = request.GET.get("page", 1)
        child_bom_list = []
        if bom_query:
            if item_id:
                pid = item_id
            else:
                pid = bom_query.first().id
            parent = BomModel.objects.get(id=pid)
            pagination = Pagination(bom_query, request.pagesizes, page)
            child_bom = BomModel.objects.filter(parent_id=pid, effective_end__gte=timezone.now())
            for i in child_bom:
                adict = {}
                adict["id"] = i.id
                adict["item"] = i.item.nr
                adict["nr"] = i.nr
                adict["parent"] = parent.nr
                adict["effective_start"] = i.effective_start
                adict["effective_end"] = i.effective_end
                adict["qty"] = i.qty
                child_bom_list.append(adict)
            content = {
                "parent_id": pid,
                "parent": parent.nr,
                "pg": pagination,
                "data": node_data,
                "child_bom_list": child_bom_list,
                "query": fs,
                "query_url": request.session.get("bom_query_url", None) if request.session.get("bom_query_url",
                                                                                               None) else "",
                "select_op": select_op,
                "select_field": self.select_field,
                "perm": request.perm,
                "error": ""
            }
        else:
            content = {
                "parent_id": "",
                "parent": "",
                "pg": pagination,
                "nodes": pagination.get_objs(),
                "data": node_data,
                "child_bom_list": child_bom_list,
                "query": fs,
                "query_url": request.session.get("bom_query_url", None) if request.session.get("bom_query_url",
                                                                                               None) else "",
                "select_op": select_op,
                "select_field": self.select_field,
                "perm": request.perm,
                "error": ""
            }
        return content


class ItemBomAdd(View):
    items = BomNr.get_nr()

    def get(self, request, *args, **kwargs):
        content = {
            "item": self.items,
            "parent": self.items
        }
        return TemplateResponse(request, "my_app_template/bom_add.html", content)

    def post(self, request, *args, **kwargs):
        form = ItemBomForm(request.POST)
        form_get = request.POST.dict()
        item = form_get["item"]
        parent = form_get["parent"]
        nr = form_get["nr"]
        # 生效开始和生效结束可能为空
        start = datetime(datetime.now().year, datetime.now().month, datetime.now().day)
        end = datetime(2030, 12, 31)
        effective_start = form_get["effective_start"] if form_get["effective_start"] else datetime.strftime(start,
                                                                                                            "%Y-%m-%d")
        effective_end = form_get["effective_end"] if form_get["effective_end"] else datetime.strftime(end, "%Y-%m-%d")
        qty = form_get["qty"]
        content = {
            "item": self.items,
            "parent": self.items,
            "parent_id": int(parent) if parent else "",
            "item_id": int(item),
            "nr": nr,
            "effective_start": effective_start,
            "effective_end": effective_end,
            "qty": qty,
            "error": ""
        }

        if form.is_valid():
            if item == parent:
                content["error"] = "物料和父类信息冲突，请重新填写"
                return TemplateResponse(request, "my_app_template/bom_add.html", content)
            try:
                if parent:
                    item_parent = BomModel.objects.filter(id=parent)
                    if not item_parent:
                        content["error"] = "请先创建父类信息"
                        return TemplateResponse(request, "my_app_template/bom_add.html", content)
                    BomModel.objects.create(nr=nr, item_id=item, parent_id=parent, effective_end=effective_end,
                                            effective_start=effective_start, qty=qty)
                else:
                    BomModel.objects.create(nr=nr, item_id=item, effective_end=effective_end,
                                            effective_start=effective_start, qty=qty)
            except:
                content["error"] = "数据已经存在，请重新填写数据"
                return TemplateResponse(request, "my_app_template/bom_add.html", content)
            else:
                return TemplateResponse(request, "my_app_template/bom_add.html", content)
        else:
            content["error"] = "表单错误"
            return TemplateResponse(request, "my_app_template/bom_add.html", content)


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
            wb = Workbook(write_only=True)
            title = "bom计算"
            ws1 = wb.create_sheet("采购物料")
            ws2 = wb.create_sheet("制造物料")
            header_ws1 = []
            header_ws2 = []
            header1 = []
            header2 = []

            common_headers = ("物料", "物料数量")
            purchase_headers = ("采购物料", "数量")
            manufacture_headers = ("制造物料", "数量")
            body_fields = ("name", "qty")

            for i in common_headers:
                cell = WriteOnlyCell(ws1, value=i)
                header_ws1.append(cell)
            ws1.append(header_ws1)
            cell1 = WriteOnlyCell(ws1, value=data["item"])
            cell2 = WriteOnlyCell(ws1, value=data["qty"])
            body_ws1 = [cell1, cell2]
            ws1.append(body_ws1)

            if data['purchase']:
                for h in purchase_headers:
                    cell = WriteOnlyCell(ws1, value=h)
                    header1.append(cell)
                ws1.append(header1)
                for i in data['purchase']:
                    body = []
                    for field in body_fields:
                        if field in i:
                            cell = WriteOnlyCell(ws1, value=i[field])
                            body.append(cell)
                    ws1.append(body)

            for i in common_headers:
                cell = WriteOnlyCell(ws2, value=i)
                header_ws2.append(cell)
            ws2.append(header_ws2)
            cell1 = WriteOnlyCell(ws2, value=data["item"])
            cell2 = WriteOnlyCell(ws2, value=data["qty"])
            body_ws2 = [cell1, cell2]
            ws2.append(body_ws2)

            if data['manufacture']:
                for h in manufacture_headers:
                    cell = WriteOnlyCell(ws2, value=h)
                    header2.append(cell)
                ws2.append(header2)
                for i in data['manufacture']:
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
        purchase = item.get_leafnodes().filter(effective_end__gte=timezone.now())
        child = item.get_descendants().filter(effective_end__gte=timezone.now())

        if list(purchase) == list(child):
            for i in purchase:
                adict = {}
                adict["qty"] = i.qty * number * item.qty
                adict["name"] = i.name
                purchase_list.append(adict)

        else:
            def get_qty(item, qty):
                qty_child = qty
                for i in item.get_children().filter(effective_end__gte=timezone.now()):
                    qty_math = i.qty * qty
                    adict = {"name": i.name, "qty": qty_math}
                    if i.is_leaf_node():
                        purchase_list.append(adict)
                        qty_child = get_qty(i, qty_math)
                    else:
                        manufacture_list.append(adict)
                        qty_child = get_qty(i, qty_math)

                return qty_child

            get_qty(item, item.qty * number)
            print(purchase_list)
            print(manufacture_list)

        content = {
            "id": id,
            "item": item.name,
            "qty": number,
            "purchase": purchase_list,
            "manufacture": manufacture_list
        }
        return content


class BomDelete(View):
    def get(self, request, *args, **kwargs):
        id = request.GET.get("id", None)
        if id:
            try:
                item = Tree_Model.objects.get(id=id)
            except:
                return HttpResponseRedirect("/bom/?msg=找不到此数据")
            else:
                content = {
                    "id": id,
                    "item": item.name,
                    "parent": item.parent.name if item.parent else "",
                    "effective_start": datetime.strftime(item.effective_start, "%Y-%m-%d"),
                    "effective_end": datetime.strftime(item.effective_start, "%Y-%m-%d"),
                    "qty": item.qty
                }
                return TemplateResponse(request, "bom_delete.html", content)
        else:
            return HttpResponseRedirect("/bom?msg=找不到数据")

    def post(self, request, *args, **kwargs):
        id = request.POST['id']
        parent = request.POST['parent']
        item = request.POST['item']
        effective_start = request.POST['effective_start']
        effective_end = request.POST['effective_end']
        qty = request.POST["qty"]

        content = {
            "id": id,
            "item": item,
            "parent": parent,
            "effective_start": effective_start,
            "effective_end": effective_end,
            "qty": qty,
            "perm": request.perm,
        }

        with transaction.atomic(savepoint=False):
            # 创建保存点
            try:
                item_node = Tree_Model.objects.get(id=id)
                # 判断当前删除的节点是否为根节点，如果为根节点直接删除当前节点
                if not item_node.is_root_node():
                    nodes = Tree_Model.objects.filter(name=item)
                    root = False
                    # 当前节点不是根节点，但是存在是根节点的关系，删除当前节点
                    for i in nodes:
                        if i.is_root_node():
                            root = True
                            break
                    if root:
                        item_node.delete()
                    # 当前节点不存在是根节点的情况，删除所有
                    else:
                        nodes.delete()
                else:
                    item_node.delete()

            except Exception as e:
                traceback.print_exc()
                content["error"] = "删除失败"
                return TemplateResponse(request, "bom_delete.html", content)

            else:
                return HttpResponseRedirect('/bom/')
