from rest_framework.filters import SearchFilter


class IngredientSearchFilter(SearchFilter):
    """Фильтр для Ингредиентов"""

    search_param = 'name'
