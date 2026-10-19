from django.db import models

class City(models.Model):
    
    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="اسم المدينة",
        help_text="ادخل اسم المدينة. يجب أن يكون فريداً ولا يقل عن 3 أحرف."
    )

    active = models.BooleanField(
        default=True,
        verbose_name="متاحة للاختيار",
        choices=[(False, 'غير متاحة'), (True, 'متاحة'),],
        help_text="تحديد ما إذا كانت المدينة متاحة للاختيار أم لا."
    )
    priority = models.PositiveIntegerField(
        default=0,
        verbose_name="الأولوية",
        help_text="تحديد أولوية المدينة. كلما زادت القيمة، زادت الأولوية."
        
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "مدينة"
        verbose_name_plural = "المدن"
        ordering = ["-priority"]