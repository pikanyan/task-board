# backend/board/views.py
from django.urls import reverse, reverse_lazy

from django_tables2 import SingleTableView
from django.views.generic import DetailView, CreateView, UpdateView, DeleteView

from django.db.models.deletion import ProtectedError

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



# Department 更新 (U)
class DepartmentUpdateView(UpdateView):
    model = models.Department

    fields = ["name", "uses_lot", "lot_g"]

    # C と共通
    template_name = "board/department_form.html"
    


    def get_success_url(self):
        return reverse("department_detail", kwargs={"pk": self.object.pk})



# Department 削除 (D)
class DepartmentDeleteView(DeleteView):
    model = models.Department

    template_name = "board/department_confirm_delete.html"

    success_url = reverse_lazy("department_list")



    def form_valid(self, form):
        # 参照されていて消せない場合をガード
        try:
            return super().form_valid(form)
        
        except ProtectedError:
            form.add_error(None, "この Department は参照されているため削除できません。")

            return self.form_invalid(form)
