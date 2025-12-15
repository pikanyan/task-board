# backend/board/urls.py
from django.urls import path
from board import views



urlpatterns =\
[
    path("departments/new/", views.DepartmentCreateView.as_view(), name="department_create"),
    path("departments/", views.DepartmentListView.as_view(), name="department_list"),
    path("departments/<int:pk>/", views.DepartmentDetailView.as_view(), name="department_detail"),
    path("departments/<int:pk>/edit/", views.DepartmentUpdateView.as_view(), name="department_update"),

    # 追加
    path("departments/<int:pk>/delete/", views.DepartmentDeleteView.as_view(), name="department_delete"),
]
