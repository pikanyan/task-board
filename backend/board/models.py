# backend/board/models.py
from django.db import models

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator



class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)

    # ロット運用するか
    uses_lot = models.BooleanField(default=False)

    # ロット基準(g)
    # uses_lot=False の時は 0 に固定

    # PositiveIntegerField という名前だが、実際は負数禁止
    lot_g = models.PositiveIntegerField(default=0)



    def __str__(self) -> str:
        return self.name



    def clean(self):
        super().clean()



        errors = {}

        if self.name is None or self.name.strip() == "":
            errors["name"] = "name を空白にはできません。"



        if self.uses_lot:
            if self.lot_g is None or self.lot_g <= 0:
                errors["lot_g"] = "uses_lot=True の場合、lot_g は 1 以上が必要です。"

        else:
            if self.lot_g != 0:
                errors["lot_g"] = "uses_lot=False の場合、lot_g は 0 にしてください。"



        if errors:
            raise ValidationError(errors)



class Item(models.Model):
    name = models.CharField(max_length=200, unique=True)

    # 1 単位が何 g か
    # 0 は禁止
    weight_per_unit_g = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    default_department = models.ForeignKey\
    (
        "Department",
        on_delete=models.PROTECT,
        null=False,
        blank=False,
    )

    is_department_output = models.BooleanField(null=False, blank=False)



    def __str__(self) -> str:
        return self.name



    def clean(self):
        super().clean()

        errors = {}



        if self.name is None or self.name.strip() == "":
            errors["name"] = "name を空白にはできません。"

        if self.weight_per_unit_g is None or self.weight_per_unit_g <= 0:
            errors["weight_per_unit_g"] = "weight_per_unit_g は 1 以上を指定してください。"

        if self.default_department_id is None:
            errors["default_department"] = "default_department を空白にはできません。"

        if self.is_department_output is None:
            errors["is_department_output"] = "is_department_output を空白にはできません。"



        if errors:
            raise ValidationError(errors)
