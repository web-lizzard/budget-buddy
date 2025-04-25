from application.dtos import DTO, CategoryDTO


class CategoryListDTO(DTO):
    categories: list[CategoryDTO]
