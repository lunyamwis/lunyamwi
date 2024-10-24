from django.shortcuts import get_object_or_404
from .models import Role


class PromptFactory:

    problems = []
    solutions = []

    def __init__(self, salesrep,outsourced_data,product,prompt) -> None:
        self.salesrep = get_object_or_404(Role,name=salesrep).name
        self.outsourced_data = outsourced_data
        self.prompt = prompt
    

    def get_problems(self, data):
        for key in self.outsourced_data.keys():
            if key in data.get("checklist"):
                pass
        return 

    def get_solutions(self):
        pass