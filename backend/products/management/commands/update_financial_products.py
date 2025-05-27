from django.core.management.base import BaseCommand
from products.utils import update_all_financial_products, fetch_products_by_type
import time
import json


class Command(BaseCommand):
    help = "Updates financial products data from external APIs"

    def add_arguments(self, parser):
        parser.add_argument(
            "--type",
            type=str,
            choices=["deposit", "saving", "mortgage", "credit", "rent", "all"],
            default="all",
            help="Type of financial products to update",
        )
        parser.add_argument(
            "--verbose",
            action="store_true",
            help="Print detailed results",
        )

    def handle(self, *args, **options):
        product_type = options["type"]
        verbose = options["verbose"]

        self.stdout.write(
            self.style.SUCCESS(f"Starting update of {product_type} products...")
        )

        start_time = time.time()

        if product_type == "all":
            results = update_all_financial_products()
        else:
            results = fetch_products_by_type([product_type])

        # Print results
        if verbose:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Detailed Results:\n{json.dumps(results, indent=2, ensure_ascii=False)}"
                )
            )
        else:
            # Print summary
            summary = results.get("summary", {})
            self.stdout.write(
                self.style.SUCCESS(
                    f"Update completed in {summary.get('total_time_taken', 'unknown')} time"
                )
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f"Total products updated: {summary.get('total_updated', 0)}"
                )
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f"All operations successful: {summary.get('all_success', False)}"
                )
            )  # Print individual results
            for product_name, result in results.items():
                if product_name != "summary":
                    status = "SUCCESS" if result.get("success", False) else "FAILED"
                    count = result.get("count", 0)
                    time_taken = result.get("time_taken", "unknown")

                    if result.get("success", False):
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"{status}: {product_name} - {count} products in {time_taken}"
                            )
                        )
                    else:
                        self.stdout.write(
                            self.style.ERROR(
                                f"{status}: {product_name} - Failed in {time_taken}"
                            )
                        )

        total_time = time.time() - start_time
        self.stdout.write(
            self.style.SUCCESS(f"Command completed in {total_time:.2f} seconds")
        )
