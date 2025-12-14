# backend/board/models.py
from django.db import models
from django.core.exceptions import ValidationError



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
