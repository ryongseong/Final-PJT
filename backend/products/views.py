from django.shortcuts import get_object_or_404
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from .utils import (
    update_all_financial_products,
    fetch_deposit_products,
    fetch_saving_products,
    fetch_mortgage_loan_products,
    fetch_credit_loan_products,
)
from .models import (
    FinancialProduct,
    DepositProduct,
    SavingProduct,
    LoanProduct,
    UserProduct,
)
from .serializers import (
    FinancialProductSerializer,
    DepositProductSerializer,
    SavingProductSerializer,
    LoanProductSerializer,
    DepositProductDetailSerializer,
    SavingProductDetailSerializer,
    LoanProductDetailSerializer,
    UserProductSerializer,
)


# Financial Products ViewSets
class FinancialProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = FinancialProduct.objects.all()
    serializer_class = FinancialProductSerializer
    filterset_fields = ["kor_co_nm", "fin_prdt_nm"]
    search_fields = ["kor_co_nm", "fin_prdt_nm"]
    permission_classes = [AllowAny]


class DepositProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DepositProduct.objects.all().select_related("product")
    filterset_fields = ["intr_rate_type", "save_trm"]
    search_fields = ["product__fin_prdt_nm", "product__kor_co_nm"]
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return DepositProductDetailSerializer
        return DepositProductSerializer


class SavingProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SavingProduct.objects.all().select_related("product")
    filterset_fields = ["intr_rate_type", "save_trm", "rsrv_type"]
    search_fields = ["product__fin_prdt_nm", "product__kor_co_nm"]
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return SavingProductDetailSerializer
        return SavingProductSerializer


class LoanProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = LoanProduct.objects.all().select_related("product")
    search_fields = ["product__fin_prdt_nm", "product__kor_co_nm"]
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return LoanProductDetailSerializer
        return LoanProductSerializer


# User favorite products
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_favorite_product(request, fin_prdt_cd):
    """
    Add a financial product to user's favorites
    """
    product = get_object_or_404(FinancialProduct, fin_prdt_cd=fin_prdt_cd)

    # Check if already in favorites
    favorite_exists = UserProduct.objects.filter(
        user=request.user, product=product
    ).exists()
    if favorite_exists:
        return Response(
            {"detail": "이미 관심 상품으로 등록되어 있습니다."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Add to favorites
    favorite = UserProduct(user=request.user, product=product)
    favorite.save()

    serializer = UserProductSerializer(favorite)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def remove_favorite_product(request, fin_prdt_cd):
    """
    Remove a financial product from user's favorites
    """
    product = get_object_or_404(FinancialProduct, fin_prdt_cd=fin_prdt_cd)

    try:
        favorite = UserProduct.objects.get(user=request.user, product=product)
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except UserProduct.DoesNotExist:
        return Response(
            {"detail": "관심 상품 목록에서 찾을 수 없습니다."},
            status=status.HTTP_404_NOT_FOUND,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_favorites(request):
    """
    Get a user's favorite financial products
    """
    favorites = UserProduct.objects.filter(user=request.user).select_related("product")
    serializer = UserProductSerializer(favorites, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def get_top_rate_products(request, product_type):
    """
    Get top rate financial products by type
    """
    # Get query parameters
    limit = int(request.GET.get("limit", 5))

    if product_type == "deposit":
        # For deposit products, order by highest max_rate
        products = DepositProduct.objects.select_related("product").order_by(
            "-intr_rate2"
        )[:limit]
        serializer = DepositProductSerializer(products, many=True)
    elif product_type == "saving":
        # For saving products, order by highest max_rate
        products = SavingProduct.objects.select_related("product").order_by(
            "-intr_rate2"
        )[:limit]
        serializer = SavingProductSerializer(products, many=True)
    elif product_type == "loan":
        # For loan products, order by lowest min_rate
        products = LoanProduct.objects.select_related("product").order_by("intr_rate")[
            :limit
        ]
        serializer = LoanProductSerializer(products, many=True)
    else:
        return Response(
            {"detail": "Invalid product type"}, status=status.HTTP_400_BAD_REQUEST
        )

    return Response(serializer.data)


# Advanced queries
@api_view(["GET"])
def top_interest_rate_products(request, product_type):
    """
    Get top financial products by interest rate
    product_type: 'deposit' or 'saving'
    """
    limit = int(request.GET.get("limit", 10))

    if product_type == "deposit":
        products = (
            DepositProduct.objects.all()
            .select_related("product")
            .order_by("-intr_rate2")[:limit]
        )
        serializer = DepositProductSerializer(products, many=True)
        return Response(serializer.data)
    elif product_type == "saving":
        products = (
            SavingProduct.objects.all()
            .select_related("product")
            .order_by("-intr_rate2")[:limit]
        )
        serializer = SavingProductSerializer(products, many=True)
        return Response(serializer.data)
    else:
        return Response(
            {
                "detail": "유효하지 않은 상품 유형입니다. deposit 또는 saving을 사용하세요."
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


@api_view(["GET"])
def lowest_rate_loan_products(request):
    """
    Get loan products with the lowest interest rates
    """
    limit = int(request.GET.get("limit", 10))

    # Get loan products related to mortgage options with lowest min rates
    from django.db.models import Min
    from .models import MortgageLoanOption

    mortgage_loans = (
        MortgageLoanOption.objects.values("product")
        .annotate(min_rate=Min("lend_rate_min"))
        .order_by("min_rate")[:limit]
    )

    product_ids = [item["product"] for item in mortgage_loans]
    products = LoanProduct.objects.filter(
        product__fin_prdt_cd__in=product_ids
    ).select_related("product")

    serializer = LoanProductSerializer(products, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def search_financial_products(request):
    """
    Search across all financial product types
    """
    query = request.GET.get("q", "")
    if not query:
        return Response(
            {"detail": "검색어를 입력해주세요."}, status=status.HTTP_400_BAD_REQUEST
        )

    # Search in FinancialProduct model
    financial_products = FinancialProduct.objects.filter(
        fin_prdt_nm__icontains=query
    ) | FinancialProduct.objects.filter(kor_co_nm__icontains=query)

    # Get all the IDs that match
    product_ids = financial_products.values_list("fin_prdt_cd", flat=True)

    # Find matching deposit products
    deposits = DepositProduct.objects.filter(
        product__fin_prdt_cd__in=product_ids
    ).select_related("product")
    savings = SavingProduct.objects.filter(
        product__fin_prdt_cd__in=product_ids
    ).select_related("product")
    loans = LoanProduct.objects.filter(
        product__fin_prdt_cd__in=product_ids
    ).select_related("product")

    # Serialize the results
    deposit_serializer = DepositProductSerializer(deposits, many=True)
    saving_serializer = SavingProductSerializer(savings, many=True)
    loan_serializer = LoanProductSerializer(loans, many=True)
    # Return combined results
    return Response(
        {
            "deposits": deposit_serializer.data,
            "savings": saving_serializer.data,
            "loans": loan_serializer.data,
        }
    )


# Admin API endpoints for updating financial products
@api_view(["POST"])
@permission_classes([IsAdminUser])
def update_all_products(request):
    """
    Update all financial products (admin only)
    """
    results = update_all_financial_products()
    return Response(results)


@api_view(["POST"])
@permission_classes([IsAdminUser])
def update_deposit_products(request):
    """
    Update deposit products (admin only)
    """
    success = fetch_deposit_products()
    if success:
        return Response(
            {
                "status": "success",
                "message": "예금 상품 데이터가 성공적으로 업데이트되었습니다.",
            }
        )
    return Response(
        {"status": "error", "message": "예금 상품 데이터 업데이트에 실패했습니다."},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


@api_view(["POST"])
@permission_classes([IsAdminUser])
def update_saving_products(request):
    """
    Update saving products (admin only)
    """
    success = fetch_saving_products()
    if success:
        return Response(
            {
                "status": "success",
                "message": "적금 상품 데이터가 성공적으로 업데이트되었습니다.",
            }
        )
    return Response(
        {"status": "error", "message": "적금 상품 데이터 업데이트에 실패했습니다."},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


@api_view(["POST"])
@permission_classes([IsAdminUser])
def update_mortgage_loan_products(request):
    """
    Update mortgage loan products (admin only)
    """
    success = fetch_mortgage_loan_products()
    if success:
        return Response(
            {
                "status": "success",
                "message": "주택담보대출 상품 데이터가 성공적으로 업데이트되었습니다.",
            }
        )
    return Response(
        {
            "status": "error",
            "message": "주택담보대출 상품 데이터 업데이트에 실패했습니다.",
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


@api_view(["POST"])
@permission_classes([IsAdminUser])
def update_credit_loan_products(request):
    """
    Update credit loan products (admin only)
    """
    success = fetch_credit_loan_products()
    if success:
        return Response(
            {
                "status": "success",
                "message": "신용대출 상품 데이터가 성공적으로 업데이트되었습니다.",
            }
        )
    return Response(
        {"status": "error", "message": "신용대출 상품 데이터 업데이트에 실패했습니다."},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
