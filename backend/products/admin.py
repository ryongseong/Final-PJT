from django.contrib import admin
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


# Register your models here.
@admin.register(FinancialProduct)
class FinancialProductAdmin(admin.ModelAdmin):
    list_display = ("fin_prdt_cd", "fin_prdt_nm", "kor_co_nm")
    search_fields = ("fin_prdt_nm", "kor_co_nm")


@admin.register(DepositProduct)
class DepositProductAdmin(admin.ModelAdmin):
    list_display = ("product", "save_trm", "intr_rate", "intr_rate2")
    list_filter = ("intr_rate_type", "save_trm")


@admin.register(SavingProduct)
class SavingProductAdmin(admin.ModelAdmin):
    list_display = ("product", "save_trm", "intr_rate", "intr_rate2")
    list_filter = ("intr_rate_type", "save_trm")


@admin.register(LoanProduct)
class LoanProductAdmin(admin.ModelAdmin):
    list_display = ("product",)


@admin.register(MortgageLoanOption)
class MortgageLoanOptionAdmin(admin.ModelAdmin):
    list_display = ("product", "mrtg_type", "lend_rate_min", "lend_rate_max")
    list_filter = ("mrtg_type", "rpay_type")


@admin.register(CreditLoanOption)
class CreditLoanOptionAdmin(admin.ModelAdmin):
    list_display = ("product", "crdt_prdt_type", "crdt_grad_avg")
    list_filter = ("crdt_prdt_type",)


@admin.register(RequirementOption)
class RequirementOptionAdmin(admin.ModelAdmin):
    list_display = ("product", "save_trm", "intr_rate", "intr_rate2")
    list_filter = ("save_trm",)


@admin.register(DepositProduct_JoinWay)
class DepositProductJoinWayAdmin(admin.ModelAdmin):
    list_display = ("product", "join_way")
    list_filter = ("join_way",)


@admin.register(LoanProduct_JoinWay)
class LoanProductJoinWayAdmin(admin.ModelAdmin):
    list_display = ("product", "join_way")
    list_filter = ("join_way",)


@admin.register(LendingRateOption)
class LendingRateOptionAdmin(admin.ModelAdmin):
    list_display = ("product", "rpay_type", "lend_rate_min", "lend_rate_max")
    list_filter = ("rpay_type", "lend_rate_type")


@admin.register(UserProduct)
class UserProductAdmin(admin.ModelAdmin):
    list_display = ("user", "product", "created_at")
    list_filter = ("created_at",)
    search_fields = ("user__username", "product__fin_prdt_nm")
