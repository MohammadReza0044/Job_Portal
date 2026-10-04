from django.core.management.base import BaseCommand

from matching.services.mongodb_vector_store import (
    check_connection,
    create_vector_indexes,
)


class Command(BaseCommand):
    help = "Set up MongoDB Vector Search indexes"

    def handle(self, *args, **options):
        self.stdout.write("Connecting to MongoDB...")

        check_connection()

        self.stdout.write("Creating Vector Search indexes...")

        create_vector_indexes()

        self.stdout.write(self.style.SUCCESS("MongoDB Vector Search setup complete."))
