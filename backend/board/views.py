# backend/board/views.py
from django_tables2 import SingleTableView

from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView

from board import models, tables



# Department 一覧 (R)
class DepartmentListView(SingleTableView):
    model = models.Department

    table_class = tables.DepartmentTable

    template_name = "board/department_list.html"
    
    paginate_by = 50



    def get_queryset(self):
        # 順序を固定することで、ページング警告対策
        return models.Department.objects.order_by("id")



# Department 詳細 (R)
class DepartmentDetailView(DetailView):
    model = models.Department

    template_name = "board/department_detail.html"
    
    context_object_name = "department"



# Department 作成 (C)
class DepartmentCreateView(CreateView):
    model = models.Department

    fields = ["name", "uses_lot", "lot_g"]

    template_name = "board/department_form.html"

    success_url = reverse_lazy("department_list")
