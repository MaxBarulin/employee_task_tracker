from rest_framework import serializers
from .models import Task

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ('id', 'name', 'parent', 'assignee', 'status', 'deadline')


class ImportantTaskSerializer(serializers.Serializer):
    task_name = serializers.CharField()
    deadline = serializers.DateField()
    suitable_employees = serializers.ListField(child=serializers.CharField())
