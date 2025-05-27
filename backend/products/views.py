from django.shortcuts import get_object_or_404
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from django.conf import settings

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
    UserProductSerializer,
)
from django.db.models import OuterRef, Subquery, FloatField, F, Q, Avg, Count, Max, Min
from django.db.models.functions import Round
from .ai_services import get_ai_product_recommendations
import logging

logger = logging.getLogger(__name__)


# Financial Products ViewSets
class FinancialProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = FinancialProduct.objects.all().order_by("kor_co_nm", "fin_prdt_nm")
    serializer_class = FinancialProductSerializer
    filterset_fields = ["kor_co_nm", "fin_prdt_nm", "loan_type", "join_way"]
    search_fields = ["kor_co_nm", "fin_prdt_nm", "join_member"]
    ordering_fields = ["kor_co_nm", "fin_prdt_nm"]
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = super().get_queryset()
        # Additional custom filtering
        category = self.request.query_params.get("category", None)
        if category:
            # Filter based on product category (deposit, saving, loan)
            if category.lower() == "deposit":
                queryset = queryset.filter(deposit_product__isnull=False)
            elif category.lower() == "saving":
                queryset = queryset.filter(saving_product__isnull=False)
            elif category.lower() == "loan":
                queryset = queryset.filter(loan_product__isnull=False)

        return queryset


class DepositProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = (
        DepositProduct.objects.all().select_related("product").order_by("-intr_rate2")
    )  # Default order by highest interest rate
    filterset_fields = ["intr_rate_type", "save_trm"]
    search_fields = ["product__fin_prdt_nm", "product__kor_co_nm"]
    ordering_fields = ["intr_rate", "intr_rate2", "save_trm", "product__kor_co_nm"]
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return DepositProductDetailSerializer
        return DepositProductSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filter by minimum interest rate
        min_rate = self.request.query_params.get("min_rate", None)
        if min_rate:
            try:
                min_rate = float(min_rate)
                queryset = queryset.filter(intr_rate__gte=min_rate)
            except ValueError:
                pass

        # Filter by maximum interest rate
        max_rate = self.request.query_params.get("max_rate", None)
        if max_rate:
            try:
                max_rate = float(max_rate)
                queryset = queryset.filter(intr_rate2__lte=max_rate)
            except ValueError:
                pass

        # Filter by bank name (partial match)
        bank = self.request.query_params.get("bank", None)
        if bank:
            queryset = queryset.filter(product__kor_co_nm__icontains=bank)

        return queryset


class SavingProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = (
        SavingProduct.objects.all().select_related("product").order_by("-intr_rate2")
    )  # Default order by highest interest rate
    filterset_fields = ["intr_rate_type", "save_trm", "rsrv_type"]
    search_fields = ["product__fin_prdt_nm", "product__kor_co_nm"]
    ordering_fields = [
        "intr_rate",
        "intr_rate2",
        "save_trm",
        "product__kor_co_nm",
        "rsrv_type",
    ]
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return SavingProductDetailSerializer
        return SavingProductSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filter by minimum interest rate
        min_rate = self.request.query_params.get("min_rate", None)
        if min_rate:
            try:
                min_rate = float(min_rate)
                queryset = queryset.filter(intr_rate__gte=min_rate)
            except ValueError:
                pass

        # Filter by maximum interest rate
        max_rate = self.request.query_params.get("max_rate", None)
        if max_rate:
            try:
                max_rate = float(max_rate)
                queryset = queryset.filter(intr_rate2__lte=max_rate)
            except ValueError:
                pass

        # Filter by bank name (partial match)
        bank = self.request.query_params.get("bank", None)
        if bank:
            queryset = queryset.filter(product__kor_co_nm__icontains=bank)

        # Filter by savings term (months)
        term = self.request.query_params.get("term", None)
        if term:
            try:
                term = int(term)
                queryset = queryset.filter(save_trm=term)
            except ValueError:
                pass

        return queryset


class LoanProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = (
        LoanProduct.objects.all()
        .select_related("product")
        .prefetch_related("product__mortgage_options", "product__credit_options")
    )
    filterset_fields = ["dcls_month"]  # We can filter by disclosure month
    search_fields = ["product__fin_prdt_nm", "product__kor_co_nm", "product__loan_type"]
    ordering_fields = ["product__kor_co_nm", "product__fin_prdt_nm"]
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        # Use the detail serializer for both list and retrieve to include options
        return LoanProductDetailSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filter by bank name (partial match)
        bank = self.request.query_params.get("bank", None)
        if bank:
            queryset = queryset.filter(product__kor_co_nm__icontains=bank)

        # Filter by loan type
        loan_type = self.request.query_params.get("loan_type", None)
        if loan_type:
            queryset = queryset.filter(product__loan_type__icontains=loan_type)

        # Filter by mortgage options
        has_mortgage = self.request.query_params.get("has_mortgage", None)
        if has_mortgage and has_mortgage.lower() == "true":
            queryset = queryset.filter(
                product__mortgage_options__isnull=False
            ).distinct()

        # Filter by credit options
        has_credit = self.request.query_params.get("has_credit", None)
        if has_credit and has_credit.lower() == "true":
            queryset = queryset.filter(product__credit_options__isnull=False).distinct()

        return queryset


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
    favorites = (
        UserProduct.objects.filter(user=request.user)
        .select_related(
            "product",
            "product__deposit_product",
            "product__saving_product",
            "product__loan_product",
        )
        .prefetch_related(
            "product__mortgage_options",
            "product__credit_options",
            "product__requirement_options",
        )
    )
    serializer = UserProductSerializer(favorites, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_product_recommendations(request):
    """
    Get personalized product recommendations for a user
    """
    # Get user favorites for context
    user_favorites = UserProduct.objects.filter(user=request.user).select_related(
        "product"
    )

    # If user has no favorites yet, return top rated products
    if not user_favorites.exists():
        # Get top deposit and saving products
        top_deposits = DepositProduct.objects.all().order_by("-intr_rate2")[:3]
        top_savings = SavingProduct.objects.all().order_by("-intr_rate2")[
            :3
        ]  # Get lowest rate loans
        lowest_loans = (
            LoanProduct.objects.all()
            .select_related("product")
            .prefetch_related("product__mortgage_options", "product__credit_options")[
                :3
            ]
        )

        deposit_serializer = DepositProductSerializer(top_deposits, many=True)
        saving_serializer = SavingProductSerializer(top_savings, many=True)
        loan_serializer = LoanProductDetailSerializer(lowest_loans, many=True)

        return Response(
            {
                "message": "추천 상품입니다. 관심 상품을 추가하면 더 정확한 추천을 받을 수 있습니다.",
                "recommendations": {
                    "deposits": deposit_serializer.data,
                    "savings": saving_serializer.data,
                    "loans": loan_serializer.data,
                },
            }
        )

    # Get favorite institutions
    favorite_institutions = set()
    for favorite in user_favorites:
        favorite_institutions.add(favorite.product.kor_co_nm)

    # Get product types user is interested in
    interested_in_deposits = UserProduct.objects.filter(
        user=request.user, product__deposit_product__isnull=False
    ).exists()

    interested_in_savings = UserProduct.objects.filter(
        user=request.user, product__saving_product__isnull=False
    ).exists()

    interested_in_loans = UserProduct.objects.filter(
        user=request.user, product__loan_product__isnull=False
    ).exists()

    recommendations = {}

    # Recommend products from favorite institutions and by interest
    if interested_in_deposits:
        # Find best deposit products from favorite institutions
        deposits_from_favorites = DepositProduct.objects.filter(
            product__kor_co_nm__in=favorite_institutions
        ).order_by("-intr_rate2")[:3]

        # Also find some high-rate deposits they might not have seen
        other_deposits = DepositProduct.objects.exclude(
            product__kor_co_nm__in=favorite_institutions
        ).order_by("-intr_rate2")[:2]

        # Combine the results
        recommended_deposits = list(deposits_from_favorites) + list(other_deposits)
        deposit_serializer = DepositProductSerializer(recommended_deposits, many=True)
        recommendations["deposits"] = deposit_serializer.data

    if interested_in_savings:
        # Find best saving products from favorite institutions
        savings_from_favorites = SavingProduct.objects.filter(
            product__kor_co_nm__in=favorite_institutions
        ).order_by("-intr_rate2")[:3]

        # Also find some high-rate savings they might not have seen
        other_savings = SavingProduct.objects.exclude(
            product__kor_co_nm__in=favorite_institutions
        ).order_by("-intr_rate2")[
            :2
        ]  # Combine the results
        recommended_savings = list(savings_from_favorites) + list(other_savings)
        saving_serializer = SavingProductSerializer(recommended_savings, many=True)
        recommendations["savings"] = saving_serializer.data

    if interested_in_loans:
        # Find best loan options from favorite institutions
        loans_from_favorites = (
            LoanProduct.objects.filter(product__kor_co_nm__in=favorite_institutions)
            .select_related("product")
            .prefetch_related("product__mortgage_options", "product__credit_options")[
                :3
            ]
        )

        # Also suggest some other good options
        other_loans = (
            LoanProduct.objects.exclude(product__kor_co_nm__in=favorite_institutions)
            .select_related("product")
            .prefetch_related("product__mortgage_options", "product__credit_options")[
                :2
            ]
        )

        # Combine the results
        recommended_loans = list(loans_from_favorites) + list(other_loans)
        loan_serializer = LoanProductDetailSerializer(recommended_loans, many=True)
        recommendations["loans"] = loan_serializer.data

    return Response(
        {
            "message": f"{request.user.username}님의 관심 금융 상품 기반 맞춤 추천입니다.",
            "favorite_institutions": list(favorite_institutions),
            "recommendations": recommendations,
        }
    )


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
        # For loan products, we need to consider options.
        # This is a simplified approach: fetch loans and their first mortgage option, order by min rate.
        # A more robust solution might involve aggregating min rates from all options.        # Fetch distinct loan product IDs that have mortgage options, ordered by the minimum lending rate
        mortgage_options_subquery = (
            MortgageLoanOption.objects.filter(product_id=OuterRef("product_id"))
            .order_by("lend_rate_min")
            .values("lend_rate_min")[:1]
        )

        credit_options_subquery = (
            CreditLoanOption.objects.filter(product_id=OuterRef("product_id"))
            .order_by("crdt_grad_1")
            .values("crdt_grad_1")[:1]
        )  # Changed to use crdt_grad_1

        # Annotate LoanProduct with the minimum rate from its options
        # We'll prioritize mortgage loans, then credit loans if no mortgage options exist or if their rates are not comparable
        # This example prioritizes mortgage loan rates.
        # Attempt to get the minimum mortgage loan rate
        try:
            loans_with_min_mortgage_rate = (
                LoanProduct.objects.annotate(
                    min_rate=Subquery(
                        mortgage_options_subquery, output_field=FloatField()
                    )
                )
                .filter(min_rate__isnull=False)
                .select_related("product")
                .prefetch_related(
                    "product__mortgage_options", "product__credit_options"
                )
                .order_by("min_rate")[:limit]
            )

            if not loans_with_min_mortgage_rate.exists():
                # If no mortgage loans with rates, try credit loans
                loans_with_min_credit_rate = (
                    LoanProduct.objects.annotate(
                        min_rate=Subquery(
                            credit_options_subquery, output_field=FloatField()
                        )
                    )
                    .filter(min_rate__isnull=False)
                    .select_related("product")
                    .prefetch_related(
                        "product__mortgage_options", "product__credit_options"
                    )
                    .order_by("min_rate")[:limit]
                )
                products = loans_with_min_credit_rate
            else:
                products = loans_with_min_mortgage_rate
        except Exception as e:
            # Fallback if there's an error with the rate-based sorting
            products = (
                LoanProduct.objects.all()
                .select_related("product")
                .prefetch_related(
                    "product__mortgage_options", "product__credit_options"
                )
                .order_by("product__kor_co_nm")[:limit]
            )

        serializer = LoanProductDetailSerializer(products, many=True)
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
    products = (
        LoanProduct.objects.filter(product__fin_prdt_cd__in=product_ids)
        .select_related("product")
        .prefetch_related("product__mortgage_options", "product__credit_options")
    )

    serializer = LoanProductDetailSerializer(products, many=True)
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
        )  # Search in FinancialProduct model
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
    loans = (
        LoanProduct.objects.filter(product__fin_prdt_cd__in=product_ids)
        .select_related("product")
        .prefetch_related("product__mortgage_options", "product__credit_options")
    )

    # Serialize the results
    deposit_serializer = DepositProductSerializer(deposits, many=True)
    saving_serializer = SavingProductSerializer(savings, many=True)
    loan_serializer = LoanProductDetailSerializer(loans, many=True)
    # Return combined results
    return Response(
        {
            "deposits": deposit_serializer.data,
            "savings": saving_serializer.data,
            "loans": loan_serializer.data,
        }
    )


@api_view(["GET"])
def filter_products(request):
    """
    Filter products by various criteria
    """
    # Get filter parameters
    product_type = request.GET.get("type", "all")  # deposit, saving, loan, all
    min_rate = request.GET.get("min_rate")
    max_rate = request.GET.get("max_rate")
    institution = request.GET.get("institution")
    term = request.GET.get("term")  # Savings/deposit term in months
    sort_by = request.GET.get("sort_by", "rate")  # rate, term, institution
    sort_order = request.GET.get("sort_order", "desc")  # asc, desc

    # Build query based on product type
    if product_type == "deposit" or product_type == "all":
        deposits = DepositProduct.objects.all().select_related("product")

        # Apply filters
        if min_rate:
            deposits = deposits.filter(intr_rate2__gte=float(min_rate))
        if max_rate:
            deposits = deposits.filter(intr_rate2__lte=float(max_rate))
        if institution:
            deposits = deposits.filter(product__kor_co_nm__icontains=institution)
        if term:
            deposits = deposits.filter(save_trm=int(term))

        # Apply sorting
        if sort_by == "rate":
            sort_field = "-intr_rate2" if sort_order == "desc" else "intr_rate2"
            deposits = deposits.order_by(sort_field)
        elif sort_by == "term":
            sort_field = "-save_trm" if sort_order == "desc" else "save_trm"
            deposits = deposits.order_by(sort_field)
        elif sort_by == "institution":
            sort_field = (
                "-product__kor_co_nm" if sort_order == "desc" else "product__kor_co_nm"
            )
            deposits = deposits.order_by(sort_field)
    else:
        deposits = DepositProduct.objects.none()

    if product_type == "saving" or product_type == "all":
        savings = SavingProduct.objects.all().select_related("product")

        # Apply filters
        if min_rate:
            savings = savings.filter(intr_rate2__gte=float(min_rate))
        if max_rate:
            savings = savings.filter(intr_rate2__lte=float(max_rate))
        if institution:
            savings = savings.filter(product__kor_co_nm__icontains=institution)
        if term:
            savings = savings.filter(save_trm=int(term))

        # Apply sorting
        if sort_by == "rate":
            sort_field = "-intr_rate2" if sort_order == "desc" else "intr_rate2"
            savings = savings.order_by(sort_field)
        elif sort_by == "term":
            sort_field = "-save_trm" if sort_order == "desc" else "save_trm"
            savings = savings.order_by(sort_field)
        elif sort_by == "institution":
            sort_field = (
                "-product__kor_co_nm" if sort_order == "desc" else "product__kor_co_nm"
            )
            savings = savings.order_by(sort_field)
    else:
        savings = SavingProduct.objects.none()

    if product_type == "loan" or product_type == "all":
        loans = (
            LoanProduct.objects.all()
            .select_related("product")
            .prefetch_related("product__mortgage_options", "product__credit_options")
        )

        # Apply filters
        if institution:
            loans = loans.filter(product__kor_co_nm__icontains=institution)

        # Apply sorting for loans
        if sort_by == "institution":
            sort_field = (
                "-product__kor_co_nm" if sort_order == "desc" else "product__kor_co_nm"
            )
            loans = loans.order_by(sort_field)
    else:
        loans = LoanProduct.objects.none()

    # Paginate results
    page = int(request.GET.get("page", 1))
    page_size = int(request.GET.get("page_size", 10))
    start_idx = (page - 1) * page_size
    end_idx = page * page_size  # Serialize
    deposit_serializer = DepositProductSerializer(
        deposits[start_idx:end_idx], many=True
    )
    saving_serializer = SavingProductSerializer(savings[start_idx:end_idx], many=True)
    loan_serializer = LoanProductDetailSerializer(loans[start_idx:end_idx], many=True)

    # Count total results for pagination
    total_count = {
        "deposits": deposits.count() if product_type in ["deposit", "all"] else 0,
        "savings": savings.count() if product_type in ["saving", "all"] else 0,
        "loans": loans.count() if product_type in ["loan", "all"] else 0,
    }

    return Response(
        {
            "results": {
                "deposits": deposit_serializer.data,
                "savings": saving_serializer.data,
                "loans": loan_serializer.data,
            },
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total_count": total_count,
                "total_pages": {
                    "deposits": (total_count["deposits"] + page_size - 1) // page_size,
                    "savings": (total_count["savings"] + page_size - 1) // page_size,
                    "loans": (total_count["loans"] + page_size - 1) // page_size,
                },
            },
        }
    )


@api_view(["GET"])
@permission_classes([AllowAny])
def get_gold_and_silver_prices(request):
    import requests
    from datetime import datetime, timedelta

    today = datetime.now().strftime("%Y-%m-%d")
    previous_day = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
    type = request.GET.get("type", "AG")

    response = requests.get(
        "https://prod-api.exgold.co.kr/api/v1/main/chart/period/price/domestic",
        params={"type": type, "from": previous_day, "to": today},
    )
    if response.status_code != 200:
        return Response(
            {"detail": "금/은 시세 데이터를 가져오는 데 실패했습니다."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    data = response.json()
    if not data or "data" not in data:
        return Response(
            {"detail": "유효하지 않은 금/은 시세 데이터입니다."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    return Response(data, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([AllowAny])
def get_exchange_rate(request):
    import requests
    from datetime import datetime, timedelta, timezone

    now = datetime.now()
    if now.weekday() >= 5 or now.hour < 11:
        day = now
        while True:
            day -= timedelta(days=1)
            if day.weekday() < 5:
                break
        day = day.strftime("%Y%m%d")
    else:
        day = now.strftime("%Y%m%d")

    response = requests.get(
        "https://www.koreaexim.go.kr/site/program/financial/exchangeJSON",
        params={
            "authkey": settings.EXCHANGE_RATE_API,
            "searchdate": day,
            "data": "AP01",
        },
        verify=False,
    )

    if response.status_code != 200:
        return Response(
            {"detail": "환율 데이터를 가져오는 데 실패했습니다."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    data = response.json()
    if not data:
        return Response(
            {"detail": "유효하지 않은 환율 데이터입니다."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    return Response(data, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([AllowAny])
def get_kospi_data(request):
    import requests
    import ast
    from datetime import datetime, timedelta

    now = datetime.now()

    previous_day = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d")
    response = requests.get(
        "https://m.stock.naver.com/front-api/external/chart/domestic/info",
        params={
            "symbol": "KOSPI",
            "requestType": 1,
            "startTime": previous_day,
            "endTime": now.strftime("%Y%m%d"),
            "timeframe": "day",
        },
        headers={"User-Agent": "Mozilla/5.0"},
    )

    if response.status_code != 200:
        return Response(
            {"detail": "주식 시장 데이터를 가져오는 데 실패했습니다."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    try:
        parsed_data = ast.literal_eval(response.text.strip())
    except Exception as e:
        return Response(
            {"detail": f"데이터 파싱 실패: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    if len(parsed_data) <= 1:
        return Response(
            {"detail": "유효하지 않은 주식 시장 데이터입니다."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    COLUMN_MAP = {
        "날짜": "date",
        "시가": "open",
        "고가": "high",
        "저가": "low",
        "종가": "close",
        "거래량": "volume",
        "외국인소진율": "foreign_rate",
    }

    columns = parsed_data[0]
    columns = [COLUMN_MAP.get(col, col) for col in columns]
    rows = parsed_data[1:]
    json_ready = [dict(zip(columns, row)) for row in rows]

    return Response(json_ready, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([AllowAny])
def get_kosdaq_data(request):
    import requests
    import ast
    from datetime import datetime, timedelta

    now = datetime.now()

    previous_day = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d")
    response = requests.get(
        "https://m.stock.naver.com/front-api/external/chart/domestic/info",
        params={
            "symbol": "KOSDAQ",
            "requestType": 1,
            "startTime": previous_day,
            "endTime": now.strftime("%Y%m%d"),
            "timeframe": "day",
        },
        headers={"User-Agent": "Mozilla/5.0"},
    )

    if response.status_code != 200:
        return Response(
            {"detail": "주식 시장 데이터를 가져오는 데 실패했습니다."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    try:
        parsed_data = ast.literal_eval(response.text.strip())
    except Exception as e:
        return Response(
            {"detail": f"데이터 파싱 실패: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    if len(parsed_data) <= 1:
        return Response(
            {"detail": "유효하지 않은 주식 시장 데이터입니다."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    COLUMN_MAP = {
        "날짜": "date",
        "시가": "open",
        "고가": "high",
        "저가": "low",
        "종가": "close",
        "거래량": "volume",
        "외국인소진율": "foreign_rate",
    }

    columns = parsed_data[0]
    columns = [COLUMN_MAP.get(col, col) for col in columns]
    rows = parsed_data[1:]
    json_ready = [dict(zip(columns, row)) for row in rows]

    return Response(json_ready, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([AllowAny])
def get_stock_rankings(request):
    import requests

    response = requests.post(
        "https://wts-cert-api.tossinvest.com/api/v2/dashboard/wts/overview/ranking",
        headers={
            "Content-Type": "application/json",
            "X-Xss-Protection": "1; mode=block",
            "User-Agent": "Mozilla/5.0",
            "Authorization": "Bearer YOUR_TOKEN",
        },
        json={
            "id": "biggest_total_amount",
            "filters": [
                "MARKET_CAP_GREATER_THAN_50M",
                "STOCKS_PRICE_GREATER_THAN_ONE_DOLLAR",
                "KRX_MANAGEMENT_STOCK",
            ],
            "duration": "realtime",
            "tag": "all",
        },
    )

    if response.status_code == 200:
        return Response(response.json(), status=status.HTTP_200_OK)
    return Response(
        {"detail": "주식 순위 데이터를 가져오는 데 실패했습니다."},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


@api_view(["GET"])
@permission_classes([AllowAny])
def get_stock_details(request, stock_code):
    import requests

    API_URL = f"https://wts-info-api.tossinvest.com/api/v1/c-chart/kr-s/{stock_code}/day:1?count=100&useAdjustedRate=true"

    if stock_code.startswith("U"):
        API_URL = f"https://wts-info-api.tossinvest.com/api/v1/c-chart/us-s/{stock_code}/day:1?count=100&useAdjustedRate=true"

    response = requests.get(
        API_URL,
        headers={
            "Content-Type": "application/json",
            "X-Xss-Protection": "1; mode=block",
            "User-Agent": "Mozilla/5.0",
        },
    )

    if response.status_code == 200:
        return Response(response.json(), status=status.HTTP_200_OK)
    return Response(
        {"detail": "주식 상세 정보를 가져오는 데 실패했습니다."},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
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
def batch_update_products(request):
    """
    Batch update specific types of financial products (admin only)
    Request body should contain a list of product types to update:
    { "types": ["deposit", "saving", "mortgage", "credit"] }
    """
    from .utils import fetch_products_by_type

    # Get the product types to update from the request body
    product_types = request.data.get("types", [])

    # Validate the product types
    valid_types = ["deposit", "saving", "mortgage", "credit"]
    invalid_types = [t for t in product_types if t not in valid_types]

    if invalid_types:
        return Response(
            {
                "status": "error",
                "message": f"Invalid product type(s): {', '.join(invalid_types)}. Valid types are: {', '.join(valid_types)}",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    # If no types specified, default to all
    if not product_types:
        product_types = valid_types

    # Fetch the products
    results = fetch_products_by_type(product_types)
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


@api_view(["GET"])
def get_product_statistics(request):
    """
    Get statistics about available financial products
    """
    from django.db.models import Avg, Count, Max, Min
    from django.db.models.functions import Round

    # Count products by type
    total_products = FinancialProduct.objects.count()
    deposit_count = DepositProduct.objects.count()
    saving_count = SavingProduct.objects.count()
    loan_count = LoanProduct.objects.count()
    mortgage_options_count = MortgageLoanOption.objects.count()
    credit_options_count = CreditLoanOption.objects.count()

    # Get financial institutions counts
    financial_institutions = (
        FinancialProduct.objects.values("kor_co_nm")
        .annotate(product_count=Count("fin_prdt_cd"))
        .order_by("-product_count")
    )

    # Get average interest rates for deposit products
    deposit_rates = DepositProduct.objects.aggregate(
        avg_rate=Round(Avg("intr_rate"), 2),
        avg_max_rate=Round(Avg("intr_rate2"), 2),
        min_rate=Min("intr_rate"),
        max_rate=Max("intr_rate2"),
    )

    # Get average interest rates for saving products
    saving_rates = SavingProduct.objects.aggregate(
        avg_rate=Round(Avg("intr_rate"), 2),
        avg_max_rate=Round(Avg("intr_rate2"), 2),
        min_rate=Min("intr_rate"),
        max_rate=Max("intr_rate2"),
    )

    # Get loan statistics
    mortgage_rates = MortgageLoanOption.objects.aggregate(
        avg_min_rate=Round(Avg("lend_rate_min"), 2),
        avg_max_rate=Round(Avg("lend_rate_max"), 2),
        min_rate=Min("lend_rate_min"),
        max_rate=Max("lend_rate_max"),
    )

    credit_rates = CreditLoanOption.objects.aggregate(
        avg_min_rate=Round(Avg("crdt_grad_1"), 2),
        avg_max_rate=Round(Avg("crdt_grad_10"), 2),
        min_rate=Min("crdt_grad_1"),
        max_rate=Max("crdt_grad_10"),
    )

    # Get top financial institutions by product count (limit to top 5)
    top_institutions = list(financial_institutions[:5])

    return Response(
        {
            "total_products": total_products,
            "products_by_type": {
                "deposits": deposit_count,
                "savings": saving_count,
                "loans": loan_count,
                "mortgage_options": mortgage_options_count,
                "credit_options": credit_options_count,
            },
            "deposit_rates": deposit_rates,
            "saving_rates": saving_rates,
            "mortgage_rates": mortgage_rates,
            "credit_rates": credit_rates,
            "top_institutions": top_institutions,
            "last_updated": (
                FinancialProduct.objects.latest("dcls_month").dcls_month
                if total_products > 0
                else None
            ),
        }
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_ai_recommendations_page(request):
    """
    Get dedicated AI-powered financial product recommendations based on user profile and preferences
    """
    # Get query parameters
    period = request.GET.get("period", "12")  # Default to 12 months
    try:
        period = int(period)
    except ValueError:
        period = 12

    product_type = request.GET.get("type", "all")  # deposit, saving, loan, all

    # Get user information
    user = request.user
    user_salary = user.salary if hasattr(user, "salary") and user.salary else 0
    user_money = user.money if hasattr(user, "money") and user.money else 0

    # Prepare product data for AI recommendation
    product_data_list = []

    # Filter products by type and period
    if product_type in ["deposit", "all"]:
        # Get deposit products matching period range (±3 months flexibility)
        deposit_products = DepositProduct.objects.filter(
            save_trm__lte=period + 3, save_trm__gte=period - 3
        ).order_by("-intr_rate2")[:15]

        # Format deposit products for AI
        for dp in deposit_products:
            product_data_list.append(
                {
                    "name": dp.product.fin_prdt_nm,
                    "bank": dp.product.kor_co_nm,
                    "type": "예금",
                    "interest_rate": dp.intr_rate2,
                    "period_months": dp.save_trm,
                    "join_way": dp.product.join_way,
                    "join_member": dp.product.join_member,
                    "interest_rate_type": dp.intr_rate_type,
                }
            )

    if product_type in ["saving", "all"]:
        # Get saving products matching period range
        saving_products = SavingProduct.objects.filter(
            save_trm__lte=period + 3, save_trm__gte=period - 3
        ).order_by("-intr_rate2")[:15]

        # Format saving products for AI
        for sp in saving_products:
            product_data_list.append(
                {
                    "name": sp.product.fin_prdt_nm,
                    "bank": sp.product.kor_co_nm,
                    "type": "적금",
                    "interest_rate": sp.intr_rate2,
                    "period_months": sp.save_trm,
                    "savings_type": sp.rsrv_type,
                    "join_way": sp.product.join_way,
                    "join_member": sp.product.join_member,
                    "interest_rate_type": sp.intr_rate_type,
                }
            )

    if product_type in ["loan", "all"]:
        # Load loan products
        loan_products = (
            LoanProduct.objects.all()
            .select_related("product")
            .prefetch_related("product__mortgage_options", "product__credit_options")[
                :10
            ]
        )

        # Format loan products with their options for AI
        for lp in loan_products:
            base_loan_data = {
                "name": lp.product.fin_prdt_nm,
                "bank": lp.product.kor_co_nm,
                "type": "대출",
                "loan_type": lp.product.loan_type,
                "join_way": lp.product.join_way,
                "join_member": lp.product.join_member,
            }

            # Add mortgage options if available
            if (
                hasattr(lp.product, "mortgage_options")
                and lp.product.mortgage_options.exists()
            ):
                option = lp.product.mortgage_options.all()[
                    0
                ]  # Just use first option for simplicity
                base_loan_data.update(
                    {
                        "interest_rate_min": option.lend_rate_min,
                        "interest_rate_max": option.lend_rate_max,
                        "mortgage_type": option.mrtg_type,
                        "repayment_type": option.rpay_type,
                    }
                )
                product_data_list.append(base_loan_data)

            # Add credit options if available
            elif (
                hasattr(lp.product, "credit_options")
                and lp.product.credit_options.exists()
            ):
                option = lp.product.credit_options.all()[0]
                base_loan_data.update(
                    {
                        "interest_rate_min": option.crdt_grad_1,
                        "interest_rate_max": option.crdt_grad_10,
                        "credit_product_type": option.crdt_prdt_type,
                    }
                )
                product_data_list.append(base_loan_data)

    # If no products found for AI recommendations
    if not product_data_list:
        return Response(
            {
                "status": "error",
                "message": f"No suitable products found for the specified type ({product_type}) and period ({period} months).",
            },
            status=status.HTTP_404_NOT_FOUND,
        )

    # Call OpenAI API for recommendations
    try:
        ai_result = get_ai_product_recommendations(
            user_salary, user_money, period, product_data_list
        )

        if ai_result["status"] == "success":
            # Return successful AI recommendations along with some standard data
            return Response(
                {
                    "status": "success",
                    "user_info": {
                        "salary": user_salary,
                        "money": user_money,
                        "period": period,
                    },
                    "recommendations": ai_result["recommendations"],
                    "product_count": len(product_data_list),
                    "product_types_analyzed": product_type,
                }
            )
        else:
            # Return error from AI service
            logger.error(
                f"AI recommendation error: {ai_result.get('message', 'Unknown error')}"
            )
            return Response(
                {
                    "status": "error",
                    "message": ai_result.get(
                        "message", "Error generating AI recommendations"
                    ),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    except Exception as e:
        logger.error(f"Exception in AI recommendations page: {str(e)}")
        return Response(
            {
                "status": "error",
                "message": f"Failed to generate recommendations: {str(e)}",
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
