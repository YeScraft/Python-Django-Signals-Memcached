from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver
from tasks.models import TodoItem, Category, PriorityCounter
from collections import Counter

from django.core.cache import cache


def cache_update():
    counts = Category.objects.all()
    print('cache_update: ', counts)
    counts_list = {c.name: c.todos_count for c in counts}
    return cache.set('my_cache', counts_list, 60)


@receiver(m2m_changed, sender=TodoItem.category.through)
def task_cats_added(sender, instance, action, model, **kwargs):
    if action != "post_add":
        return

    print('instance: ', instance)
    for cat in instance.category.all():
        name = cat.name

        new_count = TodoItem.objects.filter(category__name=name).count()

        # new_count = 0
        # for task in TodoItem.objects.all():
        #     new_count += task.category.filter(slug=slug).count()

        Category.objects.filter(name=name).update(todos_count=new_count)

        if cache.get('my_cache') is None:
            return print('Cache = {}')
        cache_update()


@receiver(m2m_changed, sender=TodoItem.category.through)
def task_cats_removed(sender, instance, action, model, **kwargs):
    if action != "post_remove":
        return

    cat_counter = Counter()

    for t in TodoItem.objects.all():
        for cat in t.category.all():
            cat_counter[cat.name] += 1
    print('cat_removed: ', cat_counter)

    names = []
    for name, new_count in cat_counter.items():
        print('Name: ', name, 'todos_count: ', new_count)
        Category.objects.filter(name=name).update(todos_count=new_count)
        names.append(name)
    Category.objects.exclude(name__in=names).update(todos_count=0)

    if cache.get('my_cache') is None:
        return print('Cache = {}')
    cache_update()

def set_priority(p_counter):
    print('p_counter: ', p_counter)
    for task in TodoItem.objects.all():
        if task.priority == 1:
            p_counter.p_high += 1
        if task.priority == 2:
            p_counter.p_medium += 1
        if task.priority == 3:
            p_counter.p_low += 1
    print('p_counter_exit: ', p_counter)
    return p_counter.save()


@receiver(post_save, sender=TodoItem)
def task_priority_changed(sender, instance, **kwargs):
    if not PriorityCounter.objects.exists():
        p_counter = PriorityCounter()
        return set_priority(p_counter)
    p_counter = PriorityCounter.objects.get()
    p_counter.p_high = 0
    p_counter.p_medium = 0
    p_counter.p_low = 0
    print('p_counter_delete: ', p_counter)
    return set_priority(p_counter)
