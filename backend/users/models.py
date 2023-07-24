from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    first_name = models.CharField(
        'Имя', max_length=200, blank=False, null=False
    )
    last_name = models.CharField(
        'Фамилия', max_length=200, blank=False, null=False
    )
    email = models.EmailField(
        'email адрес',
        blank=False,
        max_length=254,
        null=False,
        unique=True,
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['username']

    def __str__(self):
        return self.username


class Subscription(models.Model):
    follower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
    )

    follow = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follow',
        verbose_name='Автор',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['follower', 'follow'], name='unicue_ubscription'
            )
        ]

    def __str__(self):
        return f'{self.follower.username} подписан на {self.follow.username}'
