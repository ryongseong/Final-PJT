from django.core.management.base import BaseCommand
from products.utils import update_all_financial_products
import time


class Command(BaseCommand):
    help = "Updates financial products data from external APIs"

    def add_arguments(self, parser):
        parser.add_argument(
            "--type",
            type=str,
            choices=["deposit", "saving", "mortgage", "credit", "all"],
            default="all",
            help="Type of financial products to update",
        )

    def handle(self, *args, **options):
        product_type = options["type"]

        self.stdout.write(
            self.style.SUCCESS(f"Starting update of {product_type} products...")
        )

        start_time = time.time()

        if product_type == "all":
            results = update_all_financial_products()

            for product_type, success in results.items():
                status = "SUCCESS" if success else "FAILED"
                self.stdout.write(
                    self.style.SUCCESS(f"{status}: Updated {product_type}")
                    if success
                    else self.style.ERROR(f"{status}: Failed to update {product_type}")
                )
        else:
            from products.utils import (
                fetch_deposit_products,
                fetch_saving_products,
                fetch_mortgage_loan_products,
                fetch_credit_loan_products,
            )

            if product_type == "deposit":
                success = fetch_deposit_products()
            elif product_type == "saving":
                success = fetch_saving_products()
            elif product_type == "mortgage":
                success = fetch_mortgage_loan_products()
            elif product_type == "credit":
                success = fetch_credit_loan_products()

            status = "SUCCESS" if success else "FAILED"
            self.stdout.write(
                self.style.SUCCESS(f"{status}: Updated {product_type} products")
                if success
                else self.style.ERROR(
                    f"{status}: Failed to update {product_type} products"
                )
            )

        elapsed_time = time.time() - start_time
        self.stdout.write(self.style.SUCCESS(f"Finished in {elapsed_time:.2f} seconds"))
