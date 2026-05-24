import magic
from django.core.exceptions import ValidationError


def validate_pdf(file):
    # Check extension
    name = file.name.lower()
    if not name.endswith(".pdf"):
        raise ValidationError(
            "Only PDF files are allowed. Got: " + file.name.split(".")[-1]
        )

    # Check real file signature (magic bytes) — can't be spoofed like content_type
    header = file.read(2048)
    file.seek(0)  # reset pointer so the file can still be saved after validation
    mime = magic.from_buffer(header, mime=True)
    if mime != "application/pdf":
        raise ValidationError("File content is not a valid PDF.")

    # Check size — 5MB max
    if file.size > 5 * 1024 * 1024:
        raise ValidationError(
            "PDF must be under 5MB. Your file is " f"{file.size // (1024*1024)}MB."
        )
