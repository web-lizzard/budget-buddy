from fastapi import FastAPI

from .container import MainContainer


class ContainerizedFastAPI(FastAPI):
    """Custom FastAPI application with dependency container support."""

    def __init__(self, container: MainContainer, **kwargs):
        """Initialize the application.

        Args:
            container: Dependency container
            **kwargs: Additional arguments passed to FastAPI
        """
        super().__init__(**kwargs)
        self.container = container
