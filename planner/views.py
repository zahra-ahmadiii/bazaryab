from django.shortcuts import render
from .utils import optimize_visits

def visit_form(request):
    return render(request, "planner/form.html")

def visit_result(request):
    print("✅ تابع visit_result اجرا شد")
    if request.method == "POST":
        start_time = request.POST.get("start_time")
        end_time = request.POST.get("end_time")
        result = optimize_visits(start_time, end_time)
        print("Start:", start_time)
        print("End:", end_time)
        print("Visits:", result)
        return render(request, "planner/result.html", {"result": result})
    return render(request, "planner/form.html")
    