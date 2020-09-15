from django.contrib import admin

from tasks.models import TodoItem, Category, PriorityCounter


@admin.register(TodoItem)
class TodoItemAdmin(admin.ModelAdmin):
    list_display = ('description', 'is_completed', 'created')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('slug', 'name', 'todos_count')

@admin.register(PriorityCounter)
class PriorityCounterAdmin(admin.ModelAdmin):
    pass
