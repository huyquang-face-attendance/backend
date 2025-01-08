def create_unknown_id() -> str:
    """Create a UUID-like string filled with zeros for unknown person ID"""
    return str(UUID(int=0))