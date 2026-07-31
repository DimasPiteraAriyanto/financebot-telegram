import config


def is_user_allowed(user_id: int) -> bool:
    """Check if telegram user_id is authorized to use the bot.
    If ALLOWED_USER_IDS is empty, allow all users.
    """
    if not config.ALLOWED_USER_IDS:
        return True
    return user_id in config.ALLOWED_USER_IDS


def validate_amount(amount: float) -> bool:
    """Validate that transaction amount is positive and non-zero."""
    return amount > 0 and amount < 1_000_000_000_000


def sanitize_note(note: str, max_length: int = 100) -> str:
    """Sanitize and truncate note input string."""
    cleaned = note.strip()
    # Remove control characters or single newlines
    cleaned = " ".join(cleaned.split())
    return cleaned[:max_length]
