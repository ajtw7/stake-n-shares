from .session import engine
from .base import Base
from ..models.comparison_history import ComparisonHistory  # noqa: F401  <- force model registration

def init_db():
    Base.metadata.create_all(bind=engine)