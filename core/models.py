from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class Group(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = 'Grup'
        verbose_name_plural = 'Gruplar'
        ordering = ['name']

    def __str__(self):
        return self.name


class Student(AbstractUser):
    group = models.ForeignKey(
        'Group',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='students',
        verbose_name='Grup',
    )
    ogrenci_no = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        verbose_name='Öğrenci No',
    )

    class Meta:
        verbose_name = 'Öğrenci'
        verbose_name_plural = 'Öğrenciler'

    def __str__(self):
        return f"{self.get_full_name()} ({self.username})"


class Survey(models.Model):
    lesson_name = models.CharField(max_length=200, verbose_name='Ders Adı')
    is_active = models.BooleanField(default=False, verbose_name='Aktif')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Anket'
        verbose_name_plural = 'Anketler'
        ordering = ['-created_at']

    def __str__(self):
        return self.lesson_name

    def save(self, *args, **kwargs):
        if self.is_active:
            Survey.objects.exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)


class Rating(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='ratings')
    rater = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='given_ratings',
        verbose_name='Değerlendiren',
    )
    ratee = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='received_ratings',
        verbose_name='Değerlendirilen',
    )
    score = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='Puan',
    )
    comment = models.TextField(blank=True, verbose_name='Yorum')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Değerlendirme'
        verbose_name_plural = 'Değerlendirmeler'
        unique_together = ('survey', 'rater', 'ratee')

    def __str__(self):
        return f"{self.rater} → {self.ratee}: {self.score}"
