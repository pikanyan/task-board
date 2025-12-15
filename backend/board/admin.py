# backend/board/admin.py
from django.contrib import admin

from board import models



@admin.register(models.Department)
class DepartmentAdmin(admin.ModelAdmin):
    # 一覧に出す列
    list_display =\
    (
        "id",
        "name",
        "uses_lot",
        "lot_g",
    )

    # クリックできる列
    list_display_links = ("name",)

    # ロット運用する班だけ絞り込み
    list_filter = ("uses_lot",)

    # 名前検索
    search_fields = ("name",)

    #  編集画面の項目順を固定
    fields = ("name", "uses_lot", "lot_g")




@admin.register(models.Item)
class ItemAdmin(admin.ModelAdmin):
    list_display =\
    (
        "id",
        "name",
        "weight_per_unit_g",
        "default_department",
        "is_department_output",
    )

    list_display_links = ("name",)



@admin.register(models.ItemComponent)
class ItemComponentAdmin(admin.ModelAdmin):
    list_display =\
    (
        "id",
        "parent_item",
        "child_item",
        "child_units_per_parent_unit",
    )

    list_display_links = ("parent_item",)



@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    list_display =\
    (
        "id",
        "product_item",
        "quantity_units",
        "due_at",
        "customer_name",
    )

    list_display_links = ("product_item",)