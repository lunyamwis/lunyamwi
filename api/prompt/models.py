from django.db import models, connections
from django.shortcuts import get_object_or_404
from api.helpers.models import BaseModel
# Create your models here.


class Role(BaseModel):
    name = models.CharField(max_length=255)
    description = models.TextField()
    tone_of_voice = models.TextField()

    def __str__(self) -> str:
        return self.name


class ToneOfVoice(BaseModel):
    name = models.TextField()
    description = models.TextField()

    def __str__(self) -> str:
        return self.name

class Prompt(BaseModel):
    name = models.CharField(max_length=1024)
    # data = models.JSONField(default=dict)
    text_data = models.TextField(default='')
    # tone_of_voice = models.ForeignKey(ToneOfVoice, on_delete=models.CASCADE,
    #                                   null=True, blank=True)
    role = models.ForeignKey(Role, on_delete=models.CASCADE,
                             null=True, blank=True)
    # product = models.ForeignKey(Product, on_delete=models.CASCADE,
    #                             null=True, blank=True)
    # index = models.IntegerField(default=1)

    def __str__(self):
        return self.name

    # @property
    # def querying_info(self):
    #     queries = Query.objects.filter(prompt=self)
    #     querying_info = []
    #     for query_ in queries:
    #         company = get_object_or_404(Company, id=self.product.company.id)
    #         connect_to_external_database(company)
    #         with connections[company.name].cursor() as cursor:
    #             cursor.execute(query_.query)
    #             results = cursor.fetchall()

    #         query_data = {
    #             query_.name: results if results else query_.query
    #         }
    #         querying_info.append(query_data)

    #     return querying_info

    # @property
    # def get_problems(self):
    #     problems = Problem.objects.filter(product=self.product)
    #     sheet = GsheetSetting.objects.filter(
    #         company=self.product.company).last()
    #     problem_values = []
    #     if problems.exists():
    #         for problem in problems:
    #             problem_values.append({problem.name: execute_gsheet_formula(problem.gsheet_range,
    #                                                                         problem.gsheet_formula,
    #                                                                         spreadsheet_id=sheet.spreadsheet_id)})

    #     return problem_values

    # @property
    # def get_solutions(self):
    #     problems = Problem.objects.filter(product=self.product)
    #     sheet = GsheetSetting.objects.filter(
    #         company=self.product.company).last()

    #     solution_values = []
    #     for problem in problems:

    #         solutions = Solution.objects.filter(problem=problem)
    #         if solutions.exists():
    #             for solution in solutions:
    #                 solution_values.append({solution.name: execute_gsheet_formula(solution.gsheet_range,
    #                                                                               solution.gsheet_formula,
    #                                                                               spreadsheet_id=sheet.spreadsheet_id)})
    #     return solution_values

class Tool(BaseModel):
    name = models.CharField(max_length=255)
    is_agent = models.BooleanField(default=False)
    workflow = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Agent(BaseModel):
    name = models.CharField(max_length=1024)
    role = models.ForeignKey(Role, on_delete=models.CASCADE, null=True, blank=True)
    goal = models.TextField(null=True, blank=True)
    # prompt = models.ForeignKey(Prompt,on_delete=models.CASCADE, null=True, blank=True)
    prompt = models.ManyToManyField(Prompt,blank=True)
    tools = models.ManyToManyField(Tool,blank=True)
    workflow = models.CharField(max_length=255)
    
    def __str__(self):
        return self.name



class Task(BaseModel):
    name = models.CharField(max_length=1024)
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, null=True, blank=True)
    # prompt = models.ForeignKey(Prompt,on_delete=models.CASCADE, null=True, blank=True)
    prompt = models.ManyToManyField(Prompt, blank=True)
    tools = models.ManyToManyField(Tool, blank=True)
    expected_output = models.TextField()
    workflow = models.CharField(max_length=255)
    index = models.IntegerField(null=True,blank=True)

    def __str__(self):
        return self.name

class Endpoint(BaseModel):
    METHODS = (
        ('GET','GET'),
        ('POST','POST'),
        ('PUT','PUT')
    )
    url = models.URLField()
    method = models.CharField(max_length=255,choices=METHODS, default='GET')
    params = models.TextField(null=True, blank=True)
    headers = models.JSONField(null=True, blank=True)
    data = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return self.url

class Baton(BaseModel):
    start_key = models.CharField(max_length=255)
    end_key = models.CharField(max_length=255)
    endpoints = models.ManyToManyField(Endpoint)

    def __str__(self):
        return self.start_key+"======>"+self.end_key

class Department(BaseModel):
    name = models.CharField(max_length=1024)
    tasks = models.ManyToManyField(Task,blank=True)
    agents = models.ManyToManyField(Agent,blank=True)
    memory = models.BooleanField(default=True)
    prompt = models.ForeignKey(Prompt,on_delete=models.CASCADE, null=True, blank=True)
    next_department = models.JSONField(null=True,blank=True)
    baton = models.ForeignKey(Baton, on_delete=models.CASCADE, null=True, blank=True)
    

    def __str__(self):
        return self.name
class Query(BaseModel):
    name = models.CharField(max_length=255)
    query = models.TextField()
    prompt = models.ForeignKey(Prompt, on_delete=models.CASCADE,
                               null=True, blank=True)

    def __str__(self) -> str:
        return self.name


class ChatHistory(BaseModel):
    role = models.CharField(max_length=255)
    username_from = models.CharField(max_length=255)
    username_to= models.CharField(max_length=255)
    content = models.TextField()