import requests
import logging
from django.conf import settings
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
)

logger = logging.getLogger(__name__)

# Get API key from settings
API_KEY = getattr(settings, "FINANCIAL_API_KEY", "")


def fetch_deposit_products():
    """
    Fetch deposit product data from the financial API
    """
    url = f"http://finlife.fss.or.kr/finlifeapi/depositProductsSearch.json"
    params = {
        "auth": API_KEY,
        "topFinGrpNo": "020000",  # Deposit products category
        "pageNo": 1,
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()

        if response.status_code != 200 or "result" not in data:
            logger.error(f"API Error: {data.get('error')}")
            return False

        # Process base product list
        base_list = data["result"].get("baseList", [])
        for item in base_list:
            fin_prdt_cd = item.get("fin_prdt_cd")

            # Create or update FinancialProduct
            product, created = FinancialProduct.objects.update_or_create(
                fin_prdt_cd=fin_prdt_cd,
                defaults={
                    "kor_co_nm": item.get("kor_co_nm", ""),
                    "fin_prdt_nm": item.get("fin_prdt_nm", ""),
                    "join_way": item.get("join_way", ""),
                    "join_member": item.get("join_member", ""),
                },
            )

            # Create or update DepositProduct
            DepositProduct.objects.update_or_create(
                product=product,
                defaults={
                    "fin_co_no": item.get("fin_co_no", ""),
                    "dcls_month": item.get("dcls_month", ""),
                    "category": "예금",
                    "intr_rate_type": item.get("intr_rate_type", ""),
                    "save_trm": item.get("save_trm", 0),
                    "intr_rate": item.get("intr_rate", 0.0),
                    "intr_rate2": item.get("intr_rate2", 0.0),
                },
            )

            # Create or update join ways
            join_ways = item.get("join_way", "").split(",")
            for join_way in join_ways:
                if join_way.strip():
                    DepositProduct_JoinWay.objects.get_or_create(
                        product=product, join_way=join_way.strip()
                    )

        # Process option list
        option_list = data["result"].get("optionList", [])
        for item in option_list:
            fin_prdt_cd = item.get("fin_prdt_cd")
            try:
                product = FinancialProduct.objects.get(fin_prdt_cd=fin_prdt_cd)

                # Create or update RequirementOption
                RequirementOption.objects.update_or_create(
                    product=product,
                    save_trm=item.get("save_trm", 0),
                    intr_rate_type=item.get("intr_rate_type", ""),
                    defaults={
                        "intr_rate": item.get("intr_rate", 0.0),
                        "intr_rate2": item.get("intr_rate2", 0.0),
                    },
                )
            except FinancialProduct.DoesNotExist:
                logger.warning(f"Product with ID {fin_prdt_cd} not found for option")
                continue

        return True
    except Exception as e:
        logger.exception(f"Error fetching deposit products: {str(e)}")
        return False


def fetch_saving_products():
    """
    Fetch saving product data from the financial API
    """
    url = f"http://finlife.fss.or.kr/finlifeapi/savingProductsSearch.json"
    params = {
        "auth": API_KEY,
        "topFinGrpNo": "020000",  # Saving products category
        "pageNo": 1,
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()

        if response.status_code != 200 or "result" not in data:
            logger.error(f"API Error: {data.get('error')}")
            return False

        # Process base product list
        base_list = data["result"].get("baseList", [])
        for item in base_list:
            fin_prdt_cd = item.get("fin_prdt_cd")

            # Create or update FinancialProduct
            product, created = FinancialProduct.objects.update_or_create(
                fin_prdt_cd=fin_prdt_cd,
                defaults={
                    "kor_co_nm": item.get("kor_co_nm", ""),
                    "fin_prdt_nm": item.get("fin_prdt_nm", ""),
                    "join_way": item.get("join_way", ""),
                    "join_member": item.get("join_member", ""),
                },
            )

            # Create or update SavingProduct
            SavingProduct.objects.update_or_create(
                product=product,
                defaults={
                    "fin_co_no": item.get("fin_co_no", ""),
                    "dcls_month": item.get("dcls_month", ""),
                    "category": "적금",
                    "intr_rate_type": item.get("intr_rate_type", ""),
                    "rsrv_type": item.get("rsrv_type", ""),
                    "save_trm": item.get("save_trm", 0),
                    "intr_rate": item.get("intr_rate", 0.0),
                    "intr_rate2": item.get("intr_rate2", 0.0),
                },
            )

            # Create or update join ways
            join_ways = item.get("join_way", "").split(",")
            for join_way in join_ways:
                if join_way.strip():
                    DepositProduct_JoinWay.objects.get_or_create(
                        product=product, join_way=join_way.strip()
                    )

        # Process option list
        option_list = data["result"].get("optionList", [])
        for item in option_list:
            fin_prdt_cd = item.get("fin_prdt_cd")
            try:
                product = FinancialProduct.objects.get(fin_prdt_cd=fin_prdt_cd)

                # Create or update RequirementOption
                RequirementOption.objects.update_or_create(
                    product=product,
                    save_trm=item.get("save_trm", 0),
                    intr_rate_type=item.get("intr_rate_type", ""),
                    rsrv_type=item.get("rsrv_type", ""),
                    defaults={
                        "intr_rate": item.get("intr_rate", 0.0),
                        "intr_rate2": item.get("intr_rate2", 0.0),
                    },
                )
            except FinancialProduct.DoesNotExist:
                logger.warning(f"Product with ID {fin_prdt_cd} not found for option")
                continue

        return True
    except Exception as e:
        logger.exception(f"Error fetching saving products: {str(e)}")
        return False


def fetch_mortgage_loan_products():
    """
    Fetch mortgage loan product data from the financial API
    """
    url = f"http://finlife.fss.or.kr/finlifeapi/mortgageLoanProductsSearch.json"
    params = {
        "auth": API_KEY,
        "topFinGrpNo": "050000",  # Mortgage loan products category
        "pageNo": 1,
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()

        if response.status_code != 200 or "result" not in data:
            logger.error(f"API Error: {data.get('error')}")
            return False

        # Process base product list
        base_list = data["result"].get("baseList", [])
        for item in base_list:
            fin_prdt_cd = item.get("fin_prdt_cd")

            # Create or update FinancialProduct
            product, created = FinancialProduct.objects.update_or_create(
                fin_prdt_cd=fin_prdt_cd,
                defaults={
                    "kor_co_nm": item.get("kor_co_nm", ""),
                    "fin_prdt_nm": item.get("fin_prdt_nm", ""),
                    "join_way": item.get("join_way", ""),
                    "loan_type": "주택담보대출",
                    "join_member": item.get("join_member", ""),
                },
            )

            # Create or update LoanProduct
            LoanProduct.objects.update_or_create(
                product=product,
                defaults={
                    "fin_co_no": item.get("fin_co_no", ""),
                    "dcls_month": item.get("dcls_month", ""),
                    "loan_inci_expn": item.get("loan_inci_expn", ""),
                    "erly_rpay_fee": item.get("erly_rpay_fee", ""),
                    "dly_rate": item.get("dly_rate", ""),
                    "loan_lmt": item.get("loan_lmt", ""),
                },
            )

            # Create or update join ways
            join_ways = item.get("join_way", "").split(",")
            for join_way in join_ways:
                if join_way.strip():
                    LoanProduct_JoinWay.objects.get_or_create(
                        product=product, join_way=join_way.strip()
                    )

        # Process option list
        option_list = data["result"].get("optionList", [])
        for item in option_list:
            fin_prdt_cd = item.get("fin_prdt_cd")
            try:
                product = FinancialProduct.objects.get(fin_prdt_cd=fin_prdt_cd)

                # Create or update MortgageLoanOption
                MortgageLoanOption.objects.update_or_create(
                    product=product,
                    mrtg_type=item.get("mrtg_type", ""),
                    rpay_type=item.get("rpay_type", ""),
                    lend_rate_type=item.get("lend_rate_type", ""),
                    defaults={
                        "lend_rate_min": item.get("lend_rate_min", 0.0),
                        "lend_rate_max": item.get("lend_rate_max", 0.0),
                        "lend_rate_avg": item.get("lend_rate_avg"),
                    },
                )
            except FinancialProduct.DoesNotExist:
                logger.warning(f"Product with ID {fin_prdt_cd} not found for option")
                continue

        return True
    except Exception as e:
        logger.exception(f"Error fetching mortgage loan products: {str(e)}")
        return False


def fetch_credit_loan_products():
    """
    Fetch credit loan product data from the financial API
    """
    url = f"http://finlife.fss.or.kr/finlifeapi/creditLoanProductsSearch.json"
    params = {
        "auth": API_KEY,
        "topFinGrpNo": "050000",  # Credit loan products category
        "pageNo": 1,
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()

        if response.status_code != 200 or "result" not in data:
            logger.error(f"API Error: {data.get('error')}")
            return False

        # Process base product list
        base_list = data["result"].get("baseList", [])
        for item in base_list:
            fin_prdt_cd = item.get("fin_prdt_cd")

            # Create or update FinancialProduct
            product, created = FinancialProduct.objects.update_or_create(
                fin_prdt_cd=fin_prdt_cd,
                defaults={
                    "kor_co_nm": item.get("kor_co_nm", ""),
                    "fin_prdt_nm": item.get("fin_prdt_nm", ""),
                    "join_way": item.get("join_way", ""),
                    "loan_type": "신용대출",
                    "join_member": item.get("join_member", ""),
                },
            )

            # Create or update LoanProduct
            LoanProduct.objects.update_or_create(
                product=product,
                defaults={
                    "fin_co_no": item.get("fin_co_no", ""),
                    "dcls_month": item.get("dcls_month", ""),
                    "loan_inci_expn": item.get("loan_inci_expn", ""),
                    "erly_rpay_fee": item.get("erly_rpay_fee", ""),
                    "dly_rate": item.get("dly_rate", ""),
                    "loan_lmt": item.get("loan_lmt", ""),
                },
            )

            # Create or update join ways
            join_ways = item.get("join_way", "").split(",")
            for join_way in join_ways:
                if join_way.strip():
                    LoanProduct_JoinWay.objects.get_or_create(
                        product=product, join_way=join_way.strip()
                    )

        # Process option list
        option_list = data["result"].get("optionList", [])
        for item in option_list:
            fin_prdt_cd = item.get("fin_prdt_cd")
            try:
                product = FinancialProduct.objects.get(fin_prdt_cd=fin_prdt_cd)

                # Create or update CreditLoanOption
                CreditLoanOption.objects.update_or_create(
                    product=product,
                    crdt_prdt_type=item.get("crdt_prdt_type", ""),
                    crdt_lend_rate_type=item.get("crdt_lend_rate_type", ""),
                    defaults={
                        "crdt_grad_1": item.get("crdt_grad_1"),
                        "crdt_grad_4": item.get("crdt_grad_4"),
                        "crdt_grad_5": item.get("crdt_grad_5"),
                        "crdt_grad_6": item.get("crdt_grad_6"),
                        "crdt_grad_10": item.get("crdt_grad_10"),
                        "crdt_grad_11": item.get("crdt_grad_11"),
                        "crdt_grad_12": item.get("crdt_grad_12"),
                        "crdt_grad_13": item.get("crdt_grad_13"),
                        "crdt_grad_avg": item.get("crdt_grad_avg"),
                    },
                )
            except FinancialProduct.DoesNotExist:
                logger.warning(f"Product with ID {fin_prdt_cd} not found for option")
                continue

        return True
    except Exception as e:
        logger.exception(f"Error fetching credit loan products: {str(e)}")
        return False


def update_all_financial_products():
    """
    Update all financial products from APIs
    """
    deposit_success = fetch_deposit_products()
    saving_success = fetch_saving_products()
    mortgage_success = fetch_mortgage_loan_products()
    credit_success = fetch_credit_loan_products()

    return {
        "deposit_products": deposit_success,
        "saving_products": saving_success,
        "mortgage_loans": mortgage_success,
        "credit_loans": credit_success,
    }
