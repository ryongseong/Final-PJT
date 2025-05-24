from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import admin_views

router = DefaultRouter()
router.register(r"financial-products", views.FinancialProductViewSet)
router.register(r"deposits", views.DepositProductViewSet)
router.register(r"savings", views.SavingProductViewSet)
router.register(r"loans", views.LoanProductViewSet)

# Admin router for administrative actions
admin_router = DefaultRouter()
admin_router.register(r"financial-products", admin_views.AdminFinancialProductViewSet)
admin_router.register(r"deposits", admin_views.AdminDepositProductViewSet)
admin_router.register(r"savings", admin_views.AdminSavingProductViewSet)
admin_router.register(r"loans", admin_views.AdminLoanProductViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("admin/", include(admin_router.urls)),
    path("user/favorites/", views.get_user_favorites, name="user-favorites"),
    path(
        "user/favorites/<str:fin_prdt_cd>/add/",
        views.add_favorite_product,
        name="add-favorite",
    ),
    path(
        "user/favorites/<str:fin_prdt_cd>/remove/",
        views.remove_favorite_product,
        name="remove-favorite",
    ),
    path(
        "top-rates/<str:product_type>/", views.get_top_rate_products, name="top-rates"
    ),
    path(
        "lowest-rate-loans/", views.lowest_rate_loan_products, name="lowest-rate-loans"
    ),
    path("search/", views.search_financial_products, name="search-products"),
    path("filter/", views.filter_products, name="filter-products"),
    path("statistics/", views.get_product_statistics, name="product-statistics"),
    path(
        "recommendations/",
        views.get_product_recommendations,
        name="product-recommendations",
    ),
    # Admin endpoints for updating financial product data
    path("admin/update-all/", views.update_all_products, name="update-all-products"),
    path(
        "admin/batch-update/", views.batch_update_products, name="batch-update-products"
    ),
    path(
        "admin/update-deposits/",
        views.update_deposit_products,
        name="update-deposit-products",
    ),
    path(
        "admin/update-savings/",
        views.update_saving_products,
        name="update-saving-products",
    ),
    path(
        "admin/update-mortgage-loans/",
        views.update_mortgage_loan_products,
        name="update-mortgage-loan-products",
    ),
    path(
        "admin/update-credit-loans/",
        views.update_credit_loan_products,
        name="update-credit-loan-products",
    ),
]
