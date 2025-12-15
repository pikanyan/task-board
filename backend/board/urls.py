# backend/board/urls.py
from django.urls import path
from board import views



urlpatterns =\
[
    # 追加
    path("departments/", views.DepartmentListView.as_view(), name="department_list"),
]
