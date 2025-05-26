from rest_framework import serializers
from .models import (
    FinancialProduct,
    DepositProduct,
    SavingProduct,
    LoanProduct,
    MortgageLoanOption,
    CreditLoanOption,
    RequirementOption,
    DepositProduct_JoinWay,
    LoanProduct_JoinWay,
    LendingRateOption,
    UserProduct,
)


class FinancialProductSerializer(serializers.ModelSerializer):
    join_way = serializers.SerializerMethodField()

    class Meta:
        model = FinancialProduct
        fields = "__all__"

    def get_join_way(self, obj):
        if obj.join_way and isinstance(obj.join_way, str):
            return [s.strip() for s in obj.join_way.split(",") if s.strip()]
        return []


class DepositProductSerializer(serializers.ModelSerializer):
    financial_product = FinancialProductSerializer(source="product", read_only=True)

    class Meta:
        model = DepositProduct
        fields = "__all__"


class SavingProductSerializer(serializers.ModelSerializer):
    financial_product = FinancialProductSerializer(source="product", read_only=True)

    class Meta:
        model = SavingProduct
        fields = "__all__"


class LoanProductSerializer(serializers.ModelSerializer):
    financial_product = FinancialProductSerializer(source="product", read_only=True)

    class Meta:
        model = LoanProduct
        fields = "__all__"


class MortgageLoanOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MortgageLoanOption
        fields = "__all__"


class CreditLoanOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreditLoanOption
        fields = "__all__"


class RequirementOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequirementOption
        fields = "__all__"


class DepositProduct_JoinWaySerializer(serializers.ModelSerializer):
    class Meta:
        model = DepositProduct_JoinWay
        fields = "__all__"


class LoanProduct_JoinWaySerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanProduct_JoinWay
        fields = "__all__"


class LendingRateOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = LendingRateOption
        fields = "__all__"


class UserProductSerializer(serializers.ModelSerializer):
    financial_product = FinancialProductSerializer(source="product", read_only=True)
    deposit_info = serializers.SerializerMethodField()
    saving_info = serializers.SerializerMethodField()
    loan_info = serializers.SerializerMethodField()

    class Meta:
        model = UserProduct
        fields = "__all__"

    def get_deposit_info(self, obj):
        try:
            if hasattr(obj.product, "deposit_product"):
                return DepositProductSerializer(obj.product.deposit_product).data
            return None
        except Exception:
            return None

    def get_saving_info(self, obj):
        try:
            if hasattr(obj.product, "saving_product"):
                return SavingProductSerializer(obj.product.saving_product).data
            return None
        except Exception:
            return None

    def get_loan_info(self, obj):
        try:
            if hasattr(obj.product, "loan_product"):
                return LoanProductDetailSerializer(obj.product.loan_product).data
            return None
        except Exception:
            return None


# Detailed serializers for nested responses
class DepositProductDetailSerializer(serializers.ModelSerializer):
    product_info = FinancialProductSerializer(source="product", read_only=True)
    requirements = RequirementOptionSerializer(
        source="product.requirement_options", many=True, read_only=True
    )
    join_ways = DepositProduct_JoinWaySerializer(
        source="product.deposit_joinways", many=True, read_only=True
    )

    class Meta:
        model = DepositProduct
        exclude = ["product"]


class SavingProductDetailSerializer(serializers.ModelSerializer):
    product_info = FinancialProductSerializer(source="product", read_only=True)
    requirements = RequirementOptionSerializer(
        source="product.requirement_options", many=True, read_only=True
    )
    join_ways = DepositProduct_JoinWaySerializer(
        source="product.deposit_joinways", many=True, read_only=True
    )

    class Meta:
        model = SavingProduct
        exclude = ["product"]


class LoanProductDetailSerializer(serializers.ModelSerializer):
    product_info = FinancialProductSerializer(source="product", read_only=True)
    mortgage_options = MortgageLoanOptionSerializer(
        source="product.mortgage_options", many=True, read_only=True
    )
    credit_options = CreditLoanOptionSerializer(
        source="product.credit_options", many=True, read_only=True
    )
    lending_options = LendingRateOptionSerializer(
        source="product.lending_rate_options", many=True, read_only=True
    )
    join_ways = LoanProduct_JoinWaySerializer(
        source="product.loan_joinways", many=True, read_only=True
    )

    class Meta:
        model = LoanProduct
        exclude = ["product"]
