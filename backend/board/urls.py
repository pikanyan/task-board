# backend/board/urls.py
from django.urls import path
from board import views



urlpatterns =\
[
    path("departments/", views.DepartmentListView.as_view(), name="department_list"),

    # 追加
    path("departments/<int:pk>/", views.DepartmentDetailView.as_view(), name="department_detail"),
]
