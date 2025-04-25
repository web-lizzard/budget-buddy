from .category_dto import CategoryDTO
from .dto import DTO


class CategoryListDTO(DTO):
    categories: list[CategoryDTO]
