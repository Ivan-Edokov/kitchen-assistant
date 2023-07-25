from django.core.exceptions import ValidationError


MESSAGE = {
    'greater_zero': 'Значение не может быть равно нулю.'
}


def validator_not_zero(value):
    if value == 0:
        raise ValidationError(MESSAGE['greater_zero'])
