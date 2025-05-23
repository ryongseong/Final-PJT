from django.db import models
from django.utils import timezone


# 금융상품 기본 정보
class FinancialProduct(models.Model):
    fin_prdt_cd = models.CharField(max_length=255, primary_key=True)  # 금융상품 코드
    kor_co_nm = models.CharField(max_length=255)  # 금융회사명
    fin_prdt_nm = models.CharField(max_length=255)  # 금융상품명
    join_way = models.CharField(max_length=255)  # 가입방법
    loan_type = models.CharField(max_length=255, null=True, blank=True)  # 대출종류
    join_member = models.TextField(null=True, blank=True)  # 가입대상

    def __str__(self):
        return f"{self.fin_prdt_nm} - {self.kor_co_nm}"


# 예금상품 상세 정보
class DepositProduct(models.Model):
    product = models.OneToOneField(
        FinancialProduct,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="deposit_product",
    )
    fin_co_no = models.CharField(max_length=255)  # 금융회사 코드
    dcls_month = models.CharField(max_length=10)  # 공시 월
    category = models.CharField(max_length=50)  # 상품 카테고리 (예금, 적금 등)
    intr_rate_type = models.CharField(max_length=255)  # 금리유형
    save_trm = models.IntegerField()  # 저축 기간
    intr_rate = models.FloatField()  # 금리
    intr_rate2 = models.FloatField()  # 최고 금리

    def __str__(self):
        return f"{self.product.fin_prdt_nm} - {self.save_trm}개월"


# 적금상품 상세 정보
class SavingProduct(models.Model):
    product = models.OneToOneField(
        FinancialProduct,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="saving_product",
    )
    fin_co_no = models.CharField(max_length=255)  # 금융회사 코드
    dcls_month = models.CharField(max_length=10)  # 공시 월
    category = models.CharField(max_length=50)  # 상품 카테고리 (예금, 적금 등)
    intr_rate_type = models.CharField(max_length=255)  # 금리유형
    rsrv_type = models.CharField(max_length=100)  # 적립 유형
    save_trm = models.IntegerField()  # 저축 기간
    intr_rate = models.FloatField()  # 금리
    intr_rate2 = models.FloatField()  # 최고 금리

    def __str__(self):
        return f"{self.product.fin_prdt_nm} - {self.save_trm}개월"


# 대출상품 상세 정보
class LoanProduct(models.Model):
    product = models.OneToOneField(
        FinancialProduct,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="loan_product",
    )
    fin_co_no = models.CharField(max_length=255)  # 금융회사 코드
    dcls_month = models.CharField(max_length=10)  # 공시 월
    loan_inci_expn = models.TextField(null=True, blank=True)  # 대출 부대비용
    erly_rpay_fee = models.TextField(null=True, blank=True)  # 중도상환 수수료
    dly_rate = models.TextField(null=True, blank=True)  # 연체 이자율
    loan_lmt = models.TextField(null=True, blank=True)  # 대출 한도

    def __str__(self):
        return f"{self.product.fin_prdt_nm}"


# 담보 대출상품 상세 정보
class MortgageLoanOption(models.Model):
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey(
        FinancialProduct, on_delete=models.CASCADE, related_name="mortgage_options"
    )
    mrtg_type = models.CharField(max_length=255)  # 담보 유형
    rpay_type = models.CharField(max_length=255)  # 상환 유형
    lend_rate_type = models.CharField(max_length=255)  # 금리 유형
    lend_rate_min = models.FloatField()  # 최저 금리
    lend_rate_max = models.FloatField()  # 최고 금리
    lend_rate_avg = models.FloatField(null=True, blank=True)  # 평균 금리

    def __str__(self):
        return f"{self.product.fin_prdt_nm} - {self.mrtg_type}"


# 신용 대출상품 상세 정보
class CreditLoanOption(models.Model):
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey(
        FinancialProduct, on_delete=models.CASCADE, related_name="credit_options"
    )
    crdt_prdt_type = models.CharField(max_length=255)  # 신용상품 유형
    crdt_lend_rate_type = models.CharField(max_length=255)  # 금리 유형
    crdt_grad_1 = models.FloatField(null=True, blank=True)  # 신용등급 1
    crdt_grad_4 = models.FloatField(null=True, blank=True)  # 신용등급 4
    crdt_grad_5 = models.FloatField(null=True, blank=True)  # 신용등급 5
    crdt_grad_6 = models.FloatField(null=True, blank=True)  # 신용등급 6
    crdt_grad_10 = models.FloatField(null=True, blank=True)  # 신용등급 10
    crdt_grad_11 = models.FloatField(null=True, blank=True)  # 신용등급 11
    crdt_grad_12 = models.FloatField(null=True, blank=True)  # 신용등급 12
    crdt_grad_13 = models.FloatField(null=True, blank=True)  # 신용등급 13
    crdt_grad_avg = models.FloatField(null=True, blank=True)  # 평균 금리

    def __str__(self):
        return f"{self.product.fin_prdt_nm} - {self.crdt_prdt_type}"


# 예금/적금 상품 가입 조건
class RequirementOption(models.Model):
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey(
        FinancialProduct, on_delete=models.CASCADE, related_name="requirement_options"
    )
    save_trm = models.IntegerField()  # 저축 기간
    intr_rate_type = models.CharField(max_length=255)  # 금리 유형
    rsrv_type = models.CharField(
        max_length=100, null=True, blank=True
    )  # 적립 유형(적금상품만)
    intr_rate = models.FloatField()  # 기본 금리
    intr_rate2 = models.FloatField()  # 최고 금리

    def __str__(self):
        return f"{self.product.fin_prdt_nm} - {self.save_trm}개월"


# 금융상품 가입 여정
class DepositProduct_JoinWay(models.Model):
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey(
        FinancialProduct, on_delete=models.CASCADE, related_name="deposit_joinways"
    )
    join_way = models.CharField(max_length=255)  # 가입방법

    def __str__(self):
        return f"{self.product.fin_prdt_nm} - {self.join_way}"


class LoanProduct_JoinWay(models.Model):
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey(
        FinancialProduct, on_delete=models.CASCADE, related_name="loan_joinways"
    )
    join_way = models.CharField(max_length=255)  # 가입방법

    def __str__(self):
        return f"{self.product.fin_prdt_nm} - {self.join_way}"


# 대출 상품 옵션 (대출 대상 등 유형 분류)
class LendingRateOption(models.Model):
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey(
        FinancialProduct, on_delete=models.CASCADE, related_name="lending_rate_options"
    )
    rpay_type = models.CharField(max_length=255)  # 상환 유형
    lend_rate_type = models.CharField(max_length=255)  # 금리 유형
    lend_rate_min = models.FloatField()  # 최저 금리
    lend_rate_max = models.FloatField()  # 최고 금리
    lend_rate_avg = models.FloatField(null=True, blank=True)  # 평균 금리

    def __str__(self):
        return f"{self.product.fin_prdt_nm} - {self.rpay_type}"


# 유저 상품 관심목록
class UserProduct(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        "accounts.User", on_delete=models.CASCADE, related_name="favorite_products"
    )
    product = models.ForeignKey(
        FinancialProduct, on_delete=models.CASCADE, related_name="interested_users"
    )
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ("user", "product")

    def __str__(self):
        return f"{self.user.username} - {self.product.fin_prdt_nm}"
