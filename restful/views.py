# Create your views here.
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from input.models import Item
from my_app.models import BomModel
from restful.serializers import ItemSerializer, BomSerializer, BomCalculateSerializer
from restful.util import CustomerNumberPagination
from django.utils import timezone


class VipPermission(BasePermission):
    message = "您没有访问权限"

    def has_object_permission(self, request, view, obj):
        return False


class ItemAPIView(ListAPIView):
    # 这里需要调用接口
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    # 权限
    # permission_classes = (VipPermission,)
    ordering_fields = ('id',)
    pagination_class = CustomerNumberPagination


class ItemDetailView(RetrieveAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    # permission_classes = (VipPermission,)


class BomAPIView(ListAPIView):
    queryset = BomModel.objects.all()
    serializer_class = BomSerializer


class BomDetailView(RetrieveAPIView):
    queryset = BomModel.objects.all()
    serializer_class = BomSerializer


class BomCalculateView(APIView):
    def get(self, request, *args, **kwargs):
        ser = BomCalculateSerializer(data=request.query_params)
        ser.is_valid(raise_exception=True)
        if ser.validated_data:
            # 根据bom id获取对象
            bom_filter = BomModel.objects.filter(id=ser.validated_data['id'])
            if not bom_filter:
                return Response({"message": "查询数据出错"}, status=status.HTTP_400_BAD_REQUEST)
            bom = bom_filter.first()
            # 计算采购物料的qty
            purchase_list = []
            manufacture_list = []

            def get_qty(bom, qty):
                qty_child = qty
                # 根据bom表related_id 和有效日期查询，获取数据
                for i in BomModel.objects.filter(parent_id=bom.item.id, effective_end__gte=timezone.now()).order_by(
                        "id"):
                    qty_math = i.qty * qty
                    # 获取物料代码和所需物料的数量
                    adict = {"nr": i.item.nr, "qty": qty_math}
                    node = BomModel.objects.filter(parent_id=i.item.id, effective_end__gte=timezone.now())
                    # 判断是否是叶子节点
                    if not node:
                        # 采购物料
                        purchase_list.append(adict)
                        qty_child = get_qty(i, qty_math)
                    else:
                        # 制造物料
                        manufacture_list.append(adict)
                        qty_child = get_qty(i, qty_math)

                return qty_child

            get_qty(bom, ser.validated_data["qty"])
            content = {
                "id": ser.validated_data["id"],
                "item": bom.item.nr,
                "qty": ser.validated_data["qty"],
                "purchase": purchase_list,
                "manufacture": manufacture_list,
                "error": ""
            }

            return Response(content, status=status.HTTP_200_OK)
        else:
            return Response({"message": "请传入值请传入值"})


from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the snippet.
        return obj.owner == request.user
