import requests
import logging
import os
import time
from django.conf import settings
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
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
API_KEY = getattr(settings, "FINANCIAL_API_KEY", os.environ.get("FINANCE_API", ""))


def create_session_with_retry():
    """
    Create a requests session with retry capability
    """
    session = requests.Session()
    retry = Retry(
        total=5,
        backoff_factor=0.5,
        status_forcelist=[500, 502, 503, 504],
        allowed_methods=["GET", "POST"],
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


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
        session = create_session_with_retry()
        response = session.get(url, params=params, timeout=10)

        # Check HTTP status code first
        if response.status_code != 200:
            logger.error(f"Deposit API HTTP Error: Status Code {response.status_code}")
            return False

        # Try to parse JSON
        try:
            data = response.json()
        except ValueError:
            logger.error("Deposit API Error: Invalid JSON response")
            return False

        # Check for result key in response
        if "result" not in data:
            logger.error(
                f"Deposit API Error: Missing 'result' key in response - {data.get('error', 'Unknown error')}"
            )
            return False

        # Process base product list
        base_list = data["result"].get("baseList", [])
        for item in base_list:
            fin_prdt_cd = item.get("fin_prdt_cd")

            if not fin_prdt_cd:
                logger.warning("Skipping product with no product code")
                continue

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
            if not fin_prdt_cd:
                logger.warning("Skipping option with no product code")
                continue

            try:
                product = FinancialProduct.objects.get(fin_prdt_cd=fin_prdt_cd)

                # Convert string rate values to float
                intr_rate = 0.0
                intr_rate2 = 0.0

                if item.get("intr_rate") is not None:
                    try:
                        intr_rate = float(item.get("intr_rate"))
                    except (ValueError, TypeError):
                        intr_rate = 0.0

                if item.get("intr_rate2") is not None:
                    try:
                        intr_rate2 = float(item.get("intr_rate2"))
                    except (ValueError, TypeError):
                        intr_rate2 = 0.0

                # Create or update DepositProduct based on option data
                DepositProduct.objects.update_or_create(
                    product=product,
                    defaults={
                        "fin_co_no": item.get("fin_co_no", ""),
                        "dcls_month": item.get("dcls_month", ""),
                        "category": "예금",
                        "intr_rate_type": item.get("intr_rate_type", ""),
                        "save_trm": item.get("save_trm", 0),
                        "intr_rate": intr_rate,
                        "intr_rate2": intr_rate2,
                    },
                )

                # Create or update RequirementOption
                RequirementOption.objects.update_or_create(
                    product=product,
                    save_trm=item.get("save_trm", 0),
                    intr_rate_type=item.get("intr_rate_type", ""),
                    defaults={
                        "rsrv_type": "",  # Default empty string for deposit products
                        "intr_rate": intr_rate,
                        "intr_rate2": intr_rate2,
                    },
                )
            except FinancialProduct.DoesNotExist:
                logger.warning(f"Product with ID {fin_prdt_cd} not found for option")
                continue

        return True
    except requests.exceptions.Timeout:
        logger.error("Deposit API request timed out")
        return False
    except requests.exceptions.ConnectionError:
        logger.error("Deposit API connection error - server may be unreachable")
        return False
    except requests.exceptions.RequestException as e:
        logger.error(f"Deposit API request error: {str(e)}")
        return False
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
        session = create_session_with_retry()
        response = session.get(url, params=params, timeout=10)

        # Check HTTP status code first
        if response.status_code != 200:
            logger.error(f"Saving API HTTP Error: Status Code {response.status_code}")
            return False

        # Try to parse JSON
        try:
            data = response.json()
        except ValueError:
            logger.error("Saving API Error: Invalid JSON response")
            return False

        # Check for result key in response
        if "result" not in data:
            logger.error(
                f"Saving API Error: Missing 'result' key in response - {data.get('error', 'Unknown error')}"
            )
            return False

        # Process base product list
        base_list = data["result"].get("baseList", [])
        for item in base_list:
            fin_prdt_cd = item.get("fin_prdt_cd")

            if not fin_prdt_cd:
                logger.warning("Skipping product with no product code")
                continue

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

            if not fin_prdt_cd:
                logger.warning("Skipping option with no product code")
                continue

            # Convert string rate values to float
            intr_rate = 0.0
            intr_rate2 = 0.0

            if item.get("intr_rate") is not None:
                try:
                    intr_rate = float(item.get("intr_rate"))
                except (ValueError, TypeError):
                    intr_rate = 0.0

            if item.get("intr_rate2") is not None:
                try:
                    intr_rate2 = float(item.get("intr_rate2"))
                except (ValueError, TypeError):
                    intr_rate2 = 0.0

            try:
                product = FinancialProduct.objects.get(fin_prdt_cd=fin_prdt_cd)

                # Create or update SavingProduct based on option data
                SavingProduct.objects.update_or_create(
                    product=product,
                    defaults={
                        "fin_co_no": item.get("fin_co_no", ""),
                        "dcls_month": item.get("dcls_month", ""),
                        "category": "적금",
                        "intr_rate_type": item.get("intr_rate_type", ""),
                        "rsrv_type": item.get("rsrv_type", ""),
                        "save_trm": item.get("save_trm", 0),
                        "intr_rate": intr_rate,
                        "intr_rate2": intr_rate2,
                    },
                )

                # Create or update RequirementOption
                RequirementOption.objects.update_or_create(
                    product=product,
                    save_trm=item.get("save_trm", 0),
                    intr_rate_type=item.get("intr_rate_type", ""),
                    defaults={
                        "rsrv_type": item.get("rsrv_type", ""),
                        "intr_rate": intr_rate,
                        "intr_rate2": intr_rate2,
                    },
                )
            except FinancialProduct.DoesNotExist:
                logger.warning(f"Product with ID {fin_prdt_cd} not found for option")
                continue

        return True
    except requests.exceptions.Timeout:
        logger.error("Saving API request timed out")
        return False
    except requests.exceptions.ConnectionError:
        logger.error("Saving API connection error - server may be unreachable")
        return False
    except requests.exceptions.RequestException as e:
        logger.error(f"Saving API request error: {str(e)}")
        return False
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
        session = create_session_with_retry()
        response = session.get(url, params=params, timeout=10)

        # Check HTTP status code first
        if response.status_code != 200:
            logger.error(
                f"Mortgage Loan API HTTP Error: Status Code {response.status_code}"
            )
            return False

        # Try to parse JSON
        try:
            data = response.json()
        except ValueError:
            logger.error("Mortgage Loan API Error: Invalid JSON response")
            return False

        # Check for result key in response
        if "result" not in data:
            logger.error(
                f"Mortgage Loan API Error: Missing 'result' key in response - {data.get('error', 'Unknown error')}"
            )
            return False

        # Process base product list
        base_list = data["result"].get("baseList", [])
        for item in base_list:
            fin_prdt_cd = item.get("fin_prdt_cd")

            if not fin_prdt_cd:
                logger.warning("Skipping mortgage loan product with no product code")
                continue

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

            # Skip processing options without product code or required fields
            if not fin_prdt_cd:
                continue

            # Convert numeric fields to float with defaults
            lend_rate_min = item.get("lend_rate_min")
            lend_rate_max = item.get("lend_rate_max")
            lend_rate_avg = item.get("lend_rate_avg")

            if lend_rate_min is not None:
                try:
                    lend_rate_min = float(lend_rate_min)
                except (ValueError, TypeError):
                    lend_rate_min = 0.0
            else:
                lend_rate_min = 0.0

            if lend_rate_max is not None:
                try:
                    lend_rate_max = float(lend_rate_max)
                except (ValueError, TypeError):
                    lend_rate_max = 0.0
            else:
                lend_rate_max = 0.0

            if lend_rate_avg is not None:
                try:
                    lend_rate_avg = float(lend_rate_avg)
                except (ValueError, TypeError):
                    lend_rate_avg = None

            try:
                product = FinancialProduct.objects.get(fin_prdt_cd=fin_prdt_cd)

                # Create or update MortgageLoanOption if we have the necessary fields
                if (
                    "mrtg_type" in item
                    and "rpay_type" in item
                    and "lend_rate_type" in item
                ):
                    MortgageLoanOption.objects.update_or_create(
                        product=product,
                        mrtg_type=item.get("mrtg_type", ""),
                        rpay_type=item.get("rpay_type", ""),
                        lend_rate_type=item.get("lend_rate_type", ""),
                        defaults={
                            "lend_rate_min": lend_rate_min,
                            "lend_rate_max": lend_rate_max,
                            "lend_rate_avg": lend_rate_avg,
                        },
                    )

                # Create or update LendingRateOption for compatibility (may use only rpay_type and lend_rate_type)
                if "rpay_type" in item and "lend_rate_type" in item:
                    LendingRateOption.objects.update_or_create(
                        product=product,
                        rpay_type=item.get("rpay_type", ""),
                        lend_rate_type=item.get("lend_rate_type", ""),
                        defaults={
                            "lend_rate_min": lend_rate_min,
                            "lend_rate_max": lend_rate_max,
                            "lend_rate_avg": lend_rate_avg,
                        },
                    )
                else:
                    # For entries with only lend_rate_avg and no other fields
                    if lend_rate_avg is not None:
                        # Look for existing options to update
                        existing_options = LendingRateOption.objects.filter(
                            product=product
                        )
                        if existing_options.exists():
                            # Update all existing options with the average rate
                            existing_options.update(lend_rate_avg=lend_rate_avg)
                        else:
                            # Create a default option with just the average rate
                            LendingRateOption.objects.create(
                                product=product,
                                rpay_type="DEFAULT",
                                lend_rate_type="DEFAULT",
                                lend_rate_min=lend_rate_avg,
                                lend_rate_max=lend_rate_avg,
                                lend_rate_avg=lend_rate_avg,
                            )

            except FinancialProduct.DoesNotExist:
                logger.warning(
                    f"Product with ID {fin_prdt_cd} not found for mortgage loan option"
                )
                continue

        return True
    except requests.exceptions.Timeout:
        logger.error("Mortgage Loan API request timed out")
        return False
    except requests.exceptions.ConnectionError:
        logger.error("Mortgage Loan API connection error - server may be unreachable")
        return False
    except requests.exceptions.RequestException as e:
        logger.error(f"Mortgage Loan API request error: {str(e)}")
        return False
    except Exception as e:
        logger.exception(f"Error fetching mortgage loan products: {str(e)}")
        return False


def fetch_rent_house_loan_products():
    """
    Fetch rent house loan product data from the financial API
    """
    url = f"http://finlife.fss.or.kr/finlifeapi/rentHouseLoanProductsSearch.json"
    params = {
        "auth": API_KEY,
        "topFinGrpNo": "050000",  # Rent house loan products category
        "pageNo": 1,
    }

    try:
        session = create_session_with_retry()
        response = session.get(url, params=params, timeout=10)

        # Check HTTP status code first
        if response.status_code != 200:
            logger.error(
                f"Rent House Loan API HTTP Error: Status Code {response.status_code}"
            )
            return False

        # Try to parse JSON
        try:
            data = response.json()
        except ValueError:
            logger.error("Rent House Loan API Error: Invalid JSON response")
            return False

        # Check for result key in response
        if "result" not in data:
            logger.error(
                f"Rent House Loan API Error: Missing 'result' key in response - {data.get('error', 'Unknown error')}"
            )
            return False

        # Process base product list
        base_list = data["result"].get("baseList", [])
        for item in base_list:
            fin_prdt_cd = item.get("fin_prdt_cd")

            if not fin_prdt_cd:
                logger.warning("Skipping rent house loan product with no product code")
                continue

            # Create or update FinancialProduct
            product, created = FinancialProduct.objects.update_or_create(
                fin_prdt_cd=fin_prdt_cd,
                defaults={
                    "kor_co_nm": item.get("kor_co_nm", ""),
                    "fin_prdt_nm": item.get("fin_prdt_nm", ""),
                    "join_way": item.get("join_way", ""),
                    "loan_type": "전세자금대출",
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

            # Skip if no product code is provided
            if not fin_prdt_cd:
                logger.warning("Skipping rent house loan option with no product code")
                continue

            # Convert numeric fields to float with proper error handling
            lend_rate_min = 0.0
            lend_rate_max = 0.0
            lend_rate_avg = None

            if item.get("lend_rate_min") is not None:
                try:
                    lend_rate_min = float(item.get("lend_rate_min"))
                except (ValueError, TypeError):
                    lend_rate_min = 0.0

            if item.get("lend_rate_max") is not None:
                try:
                    lend_rate_max = float(item.get("lend_rate_max"))
                except (ValueError, TypeError):
                    lend_rate_max = 0.0

            if item.get("lend_rate_avg") is not None:
                try:
                    lend_rate_avg = float(item.get("lend_rate_avg"))
                except (ValueError, TypeError):
                    lend_rate_avg = None

            try:
                # Find the product with the matching product code
                product = FinancialProduct.objects.get(fin_prdt_cd=fin_prdt_cd)

                # Get repayment and lending rate types from the option
                rpay_type = item.get(
                    "rpay_type", "S"
                )  # Default to "S" for 만기일시상환방식
                lend_rate_type = item.get(
                    "lend_rate_type", "F"
                )  # Default to "F" for 고정금리

                # Create or update LendingRateOption
                LendingRateOption.objects.update_or_create(
                    product=product,
                    rpay_type=rpay_type,
                    lend_rate_type=lend_rate_type,
                    defaults={
                        "lend_rate_min": lend_rate_min,
                        "lend_rate_max": lend_rate_max,
                        "lend_rate_avg": lend_rate_avg,
                    },
                )
            except FinancialProduct.DoesNotExist:
                logger.warning(
                    f"Product with ID {fin_prdt_cd} not found for rent house loan option"
                )
                continue

        return True
    except requests.exceptions.Timeout:
        logger.error("Rent House Loan API request timed out")
        return False
    except requests.exceptions.ConnectionError:
        logger.error("Rent House Loan API connection error - server may be unreachable")
        return False
    except requests.exceptions.RequestException as e:
        logger.error(f"Rent House Loan API request error: {str(e)}")
        return False
    except Exception as e:
        logger.exception(f"Error fetching rent house loan products: {str(e)}")
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
        session = create_session_with_retry()
        response = session.get(url, params=params, timeout=10)

        # Check HTTP status code first
        if response.status_code != 200:
            logger.error(
                f"Credit Loan API HTTP Error: Status Code {response.status_code}"
            )
            return False

        # Try to parse JSON
        try:
            data = response.json()
        except ValueError:
            logger.error("Credit Loan API Error: Invalid JSON response")
            return False

        # Check for result key in response
        if "result" not in data:
            logger.error(
                f"Credit Loan API Error: Missing 'result' key in response - {data.get('error', 'Unknown error')}"
            )
            return False

        # Process base product list
        base_list = data["result"].get("baseList", [])
        for item in base_list:
            fin_prdt_cd = item.get("fin_prdt_cd")

            if not fin_prdt_cd:
                logger.warning("Skipping credit loan product with no product code")
                continue

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
                    "loan_inci_expn": "",  # Credit loan API doesn't provide these values
                    "erly_rpay_fee": "",
                    "dly_rate": "",
                    "loan_lmt": "",
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

            # Skip if no product code is provided
            if not fin_prdt_cd:
                logger.warning("Skipping credit loan option with no product code")
                continue

            # Safe conversion of credit grade values to float
            credit_fields = [
                "crdt_grad_1",
                "crdt_grad_4",
                "crdt_grad_5",
                "crdt_grad_6",
                "crdt_grad_10",
                "crdt_grad_11",
                "crdt_grad_12",
                "crdt_grad_13",
                "crdt_grad_avg",
            ]

            credit_data = {}
            for field in credit_fields:
                value = item.get(field)
                if value is not None:
                    try:
                        credit_data[field] = float(value)
                    except (ValueError, TypeError):
                        credit_data[field] = None
                else:
                    credit_data[field] = None

            try:
                # Find the product with the matching product code
                product = FinancialProduct.objects.get(fin_prdt_cd=fin_prdt_cd)

                # Get credit product type and lending rate type from the option
                crdt_prdt_type = item.get(
                    "crdt_prdt_type", "1"
                )  # Default to "1" for 일반신용대출
                crdt_lend_rate_type = item.get(
                    "crdt_lend_rate_type", "A"
                )  # Default to "A" for 대출금리

                # Create or update CreditLoanOption
                CreditLoanOption.objects.update_or_create(
                    product=product,
                    crdt_prdt_type=crdt_prdt_type,
                    crdt_lend_rate_type=crdt_lend_rate_type,
                    defaults={
                        "crdt_grad_1": credit_data.get("crdt_grad_1"),
                        "crdt_grad_4": credit_data.get("crdt_grad_4"),
                        "crdt_grad_5": credit_data.get("crdt_grad_5"),
                        "crdt_grad_6": credit_data.get("crdt_grad_6"),
                        "crdt_grad_10": credit_data.get("crdt_grad_10"),
                        "crdt_grad_11": credit_data.get("crdt_grad_11"),
                        "crdt_grad_12": credit_data.get("crdt_grad_12"),
                        "crdt_grad_13": credit_data.get("crdt_grad_13"),
                        "crdt_grad_avg": credit_data.get("crdt_grad_avg"),
                    },
                )
            except FinancialProduct.DoesNotExist:
                logger.warning(
                    f"Product with ID {fin_prdt_cd} not found for credit loan option"
                )
                continue

        return True
    except requests.exceptions.Timeout:
        logger.error("Credit Loan API request timed out")
        return False
    except requests.exceptions.ConnectionError:
        logger.error("Credit Loan API connection error - server may be unreachable")
        return False
    except requests.exceptions.RequestException as e:
        logger.error(f"Credit Loan API request error: {str(e)}")
        return False
    except Exception as e:
        logger.exception(f"Error fetching credit loan products: {str(e)}")
        return False


def fetch_products_by_type(product_types=None):
    """
    Fetch financial products by type
    product_types: list of product types to fetch. If None, fetch all types.
    Valid types: 'deposit', 'saving', 'mortgage', 'credit', 'rent'
    """
    from django.utils import timezone

    if product_types is None:
        product_types = ["deposit", "saving", "mortgage", "credit", "rent"]

    results = {}
    start_time = time.time()

    # Process deposit products
    if "deposit" in product_types:
        deposit_start = time.time()
        deposit_success = fetch_deposit_products()
        deposit_time = time.time() - deposit_start
        deposit_count = DepositProduct.objects.count() if deposit_success else 0
        results["deposit_products"] = {
            "success": deposit_success,
            "count": deposit_count,
            "time_taken": f"{deposit_time:.2f} seconds",
            "timestamp": timezone.now().isoformat(),
        }

    # Process saving products
    if "saving" in product_types:
        saving_start = time.time()
        saving_success = fetch_saving_products()
        saving_time = time.time() - saving_start
        saving_count = SavingProduct.objects.count() if saving_success else 0
        results["saving_products"] = {
            "success": saving_success,
            "count": saving_count,
            "time_taken": f"{saving_time:.2f} seconds",
            "timestamp": timezone.now().isoformat(),
        }

    # Process mortgage loan products
    if "mortgage" in product_types:
        mortgage_start = time.time()
        mortgage_success = fetch_mortgage_loan_products()
        mortgage_time = time.time() - mortgage_start
        mortgage_count = MortgageLoanOption.objects.count() if mortgage_success else 0
        results["mortgage_loans"] = {
            "success": mortgage_success,
            "count": mortgage_count,
            "time_taken": f"{mortgage_time:.2f} seconds",
            "timestamp": timezone.now().isoformat(),
        }

    # Process rent house loan products
    if "rent" in product_types:
        rent_start = time.time()
        rent_success = fetch_rent_house_loan_products()
        rent_time = time.time() - rent_start
        rent_count = (
            LendingRateOption.objects.filter(product__loan_type="전세자금대출").count()
            if rent_success
            else 0
        )
        results["rent_loans"] = {
            "success": rent_success,
            "count": rent_count,
            "time_taken": f"{rent_time:.2f} seconds",
            "timestamp": timezone.now().isoformat(),
        }

    # Process credit loan products
    if "credit" in product_types:
        credit_start = time.time()
        credit_success = fetch_credit_loan_products()
        credit_time = time.time() - credit_start
        credit_count = CreditLoanOption.objects.count() if credit_success else 0
        results["credit_loans"] = {
            "success": credit_success,
            "count": credit_count,
            "time_taken": f"{credit_time:.2f} seconds",
            "timestamp": timezone.now().isoformat(),
        }

    # Calculate success status
    success_results = []
    product_counts = 0

    if "deposit" in product_types:
        success_results.append(results["deposit_products"]["success"])
        product_counts += results["deposit_products"]["count"]

    if "saving" in product_types:
        success_results.append(results["saving_products"]["success"])
        product_counts += results["saving_products"]["count"]

    if "mortgage" in product_types:
        success_results.append(results["mortgage_loans"]["success"])
        product_counts += results["mortgage_loans"]["count"]

    if "rent" in product_types:
        success_results.append(results["rent_loans"]["success"])
        product_counts += results["rent_loans"]["count"]

    if "credit" in product_types:
        success_results.append(results["credit_loans"]["success"])
        product_counts += results["credit_loans"]["count"]

    # Add overall summary
    total_time = time.time() - start_time
    results["summary"] = {
        "all_success": all(success_results) if success_results else False,
        "total_time_taken": f"{total_time:.2f} seconds",
        "total_updated": product_counts,
        "timestamp": timezone.now().isoformat(),
        "types_updated": product_types,
    }

    return results


def update_all_financial_products():
    """
    Update all financial products from APIs
    Returns detailed results including success status, counts, and timestamps
    """
    return fetch_products_by_type()
