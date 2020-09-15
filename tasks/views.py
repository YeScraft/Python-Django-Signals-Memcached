from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from tasks.models import TodoItem, Category, PriorityCounter
from django.core.cache import cache

def index(request):

    # 1st version
    # counts = {t.name: random.randint(1, 100) for t in Tag.objects.all()}

    # 2nd version
    # counts = {t.name: t.taggit_taggeditem_items.count()
    # for t in Tag.objects.all()}

    # 3rd version

    # from django.db.models import Count

    from django.core.cache import cache

    if cache.get('my_cache') is None:
        counts = Category.objects.all()
        counts_list = {c.name: c.todos_count for c in counts}
        print('counts_cache:', counts_list)
        cache.set('my_cache', counts_list, 60)
        p_counts = PriorityCounter.objects.all()
        return render(request, "tasks/index.html", {"counts": counts_list, "p_counts": p_counts})

    # counts = Category.objects.annotate(total_tasks=Count(
    #     'todoitem')).order_by("-total_tasks")

    # counts = Category.objects.annotate(total_tasks=Count(
    #     'todoitem'))

    counts_list = cache.get('my_cache')
    print('counts_cache:', counts_list)
    p_counts = PriorityCounter.objects.all()
    return render(request, "tasks/index.html", {"counts": counts_list, "p_counts": p_counts})


def filter_tasks(tags_by_task):
    return set(sum(tags_by_task, []))


def tasks_by_cat(request, cat_slug=None):
    u = request.user
    tasks = TodoItem.objects.filter(owner=u).all().order_by('category')

    categories = []
    for t in tasks:
        for cat in t.category.all():
            if cat not in categories:
                categories.append(cat)

    cat = None
    if cat_slug:
        cat = get_object_or_404(Category, slug=cat_slug)
        tasks = tasks.filter(category__in=[cat])

    return render(
        request,
        "tasks/list_by_cat.html",
        {"category": cat, "tasks": tasks, "categories": categories},
    )


class TaskListView(ListView):
    model = TodoItem
    context_object_name = "tasks"
    template_name = "tasks/list.html"

    def get_queryset(self):
        u = self.request.user
        qs = super().get_queryset()
        return qs.filter(owner=u)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user_tasks = self.get_queryset().order_by('category')
        # tags = []
        categories = []
        for task in user_tasks:
            # tags.append(list(t.category.all()))
            # categories = []

            for cat in task.category.all():
                if cat not in categories:
                    categories.append(cat)

        context["categories"] = categories

        return context


class TaskDetailsView(DetailView):
    model = TodoItem
    template_name = "tasks/details.html"

def show_date(request):
    from datetime import datetime
    data = datetime.now()
    print('Data: ', data)
    return render(request, "tasks/datatime.html", {"data": data})