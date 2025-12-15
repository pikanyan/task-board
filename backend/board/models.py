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




class ItemComponent(models.Model):
    parent_item = models.ForeignKey\
    (
        "Item",
        on_delete=models.PROTECT,
        related_name="components_as_parent",
        null=False,
        blank=False,
    )

    child_item = models.ForeignKey\
    (
        "Item",
        on_delete=models.PROTECT,
        related_name="components_as_child",
        null=False,
        blank=False,
    )

    # 1 以上 を定義側でも明確化
    child_units_per_parent_unit = models.PositiveIntegerField\
    (
        validators=[MinValueValidator(1)]
    )



    class Meta:
        # (parent_item, child_item) の一意制約
        constraints =\
        [
            models.UniqueConstraint
            (
                fields=["parent_item", "child_item"],

                name="uniq_itemcomponent_parent_child",
            )
        ]



    def __str__(self) -> str:
        return f"{self.parent_item} -> {self.child_item} x {self.child_units_per_parent_unit}"



    def clean(self):
        super().clean()

        errors = {}



        if self.parent_item_id is None:
            errors["parent_item"] = "parent_item を空白にはできません。"

        if self.child_item_id is None:
            errors["child_item"] = "child_item を空白にはできません。"

        if\
        (
            self.child_units_per_parent_unit is None
            or
            self.child_units_per_parent_unit <= 0
        ):
            errors["child_units_per_parent_unit"] = ("child_units_per_parent_unit は 1 以上を指定してください。")



        if self.parent_item_id is not None and self.child_item_id is not None:
            if self.parent_item_id == self.child_item_id:
                errors["child_item"] = "parent_item と child_item を同一にはできません。"



        if errors:
            raise ValidationError(errors)




class Order(models.Model):
    product_item = models.ForeignKey\
    (
        Item,
        on_delete=models.PROTECT,
        null=False,
        blank=False,
    )

    # 1 以上 を定義側でも明確化
    quantity_units = models.PositiveIntegerField\
    (
        validators=[MinValueValidator(1)]
    )

    due_at = models.DateTimeField(null=False, blank=False)

    customer_name = models.CharField(max_length=200, null=False, blank=False)



    def __str__(self) -> str:
        return f"{self.product_item} x {self.quantity_units} @ {self.due_at} ({self.customer_name})"



    def clean(self):
        super().clean()

        errors = {}



        if self.product_item_id is None:
            errors["product_item"] = "product_item を空白にはできません。"

        if self.quantity_units is None or self.quantity_units <= 0:
            errors["quantity_units"] = "quantity_units は 1 以上を指定してください。"

        if self.due_at is None:
            errors["due_at"] = "due_at を空白にはできません。"

        if self.customer_name is None or self.customer_name.strip() == "":
            errors["customer_name"] = "customer_name を空白にはできません。"



        if errors:
            raise ValidationError(errors)



class Task(models.Model):
    department = models.ForeignKey\
    (
        Department,
        on_delete=models.PROTECT,
        null=False,
        blank=False,
    )

    item = models.ForeignKey\
    (
        Item,
        on_delete=models.PROTECT,
        null=False,
        blank=False,
    )

    # 1 以上 を定義側でも明確化
    quantity_units = models.PositiveIntegerField\
    (
        validators=[MinValueValidator(1)]
    )

    due_at = models.DateTimeField(null=False, blank=False)



    def __str__(self) -> str:
        return f"{self.department}: {self.item} x {self.quantity_units} @ {self.due_at}"



    def clean(self):
        super().clean()

        errors = {}



        if self.department_id is None:
            errors["department"] = "department を空白にはできません。"

        if self.item_id is None:
            errors["item"] = "item を空白にはできません。"

        if self.quantity_units is None or self.quantity_units <= 0:
            errors["quantity_units"] = "quantity_units は 1 以上を指定してください。"

        if self.due_at is None:
            errors["due_at"] = "due_at を空白にはできません。"



        if errors:
            raise ValidationError(errors)
