from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = "Load sample financial product data from fixtures"

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS("Loading sample financial product data...")
        )

        try:
            call_command("loaddata", "sample_products")
            self.stdout.write(
                self.style.SUCCESS("Successfully loaded sample products.")
            )
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error loading sample products: {e}"))
