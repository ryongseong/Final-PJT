from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from .models import (
    FinancialProduct,
    DepositProduct,
    SavingProduct,
    LoanProduct,
    MortgageLoanOption,
    CreditLoanOption,
)
from .serializers import (
    FinancialProductSerializer,
    DepositProductSerializer,
    SavingProductSerializer,
    LoanProductSerializer,
    DepositProductDetailSerializer,
    SavingProductDetailSerializer,
    LoanProductDetailSerializer,
)
from django.db.models import Q
from django.shortcuts import get_object_or_404


class AdminFinancialProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet for administrators to manage financial products
    """

    queryset = FinancialProduct.objects.all().order_by("kor_co_nm", "fin_prdt_nm")
    serializer_class = FinancialProductSerializer
    permission_classes = [IsAdminUser]

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return FinancialProductSerializer
        return FinancialProductSerializer

    @action(detail=False, methods=["get"], url_path="search")
    def search_products(self, request):
        query = request.query_params.get("q", "")
        category = request.query_params.get("category", "")

        queryset = self.queryset

        if query:
            queryset = queryset.filter(
                Q(fin_prdt_nm__icontains=query) | Q(kor_co_nm__icontains=query)
            )

        if category:
            if category.lower() == "deposit":
                queryset = queryset.filter(deposit_product__isnull=False)
            elif category.lower() == "saving":
                queryset = queryset.filter(saving_product__isnull=False)
            elif category.lower() == "loan":
                queryset = queryset.filter(loan_product__isnull=False)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class AdminDepositProductViewSet(viewsets.ModelViewSet):
    queryset = DepositProduct.objects.all().select_related("product")
    permission_classes = [IsAdminUser]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return DepositProductDetailSerializer
        return DepositProductSerializer


class AdminSavingProductViewSet(viewsets.ModelViewSet):
    queryset = SavingProduct.objects.all().select_related("product")
    permission_classes = [IsAdminUser]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return SavingProductDetailSerializer
        return SavingProductSerializer


class AdminLoanProductViewSet(viewsets.ModelViewSet):
    queryset = LoanProduct.objects.all().select_related("product")
    permission_classes = [IsAdminUser]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return LoanProductDetailSerializer
        return LoanProductSerializer
