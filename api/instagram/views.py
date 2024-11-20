import yaml
import os
import json
import uuid
import logging
import requests
import pandas as pd
import subprocess
from requests.auth import HTTPBasicAuth
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from django.conf import settings
from django.utils import timezone
from django.contrib import messages
from .tasks import scrap_followers,scrap_info,scrap_users,insert_and_enrich,scrap_mbo,scrap_media
from api.helpers.dag_generator import generate_dag
from api.helpers.dag_file_handler import push_file,push_file_gcp
from api.helpers.date_helper import datetime_to_cron_expression
from boostedchatScrapper.spiders.helpers.thecut_scrapper import scrap_the_cut
from boostedchatScrapper.spiders.helpers.instagram_helper import fetch_pending_inbox,approve_inbox_requests,send_direct_answer
from django.db.models import Q

from .models import InstagramUser
from django_tenants.utils import schema_context

from rest_framework import viewsets
from boostedchatScrapper.models import ScrappedData
from instagrapi import Client


from .models import Score, QualificationAlgorithm, Scheduler, AirflowCreds, InstagramUser, LeadSource,DagModel,SimpleHttpOperatorModel,HttpOperatorConnectionModel, WorkflowModel, Endpoint,CustomField,CustomFieldValue,Media,Scout

from django.shortcuts import render, redirect, get_object_or_404
from .forms import WorkflowModelForm
from .utils import generate_dag_script


# 6th
from django.contrib import messages
from django.views.generic import ListView,DeleteView,DetailView,View
from django.views.generic.edit import (
    CreateView, UpdateView
)

from .forms import (
    WorkflowModelForm, SimpleHttpOperatorFormSet, DagFormSet,HttpOperatorConnectionForm,WorkflowRunnerForm,EndpointForm,CustomFieldForm,CustomFieldValueForm
)
from django.urls import reverse_lazy
from boostedchatScrapper.spiders.helpers.instagram_login_helper import login_user

# views.py
from .serializers import (
    ScoreSerializer, 
    InstagramLeadSerializer,  
    QualificationAlgorithmSerializer, 
    SchedulerSerializer, 
    LeadSourceSerializer, 
    SimpleHttpOperatorModelSerializer, WorkflowModelSerializer,
    MediaSerializer,
    CustomFieldSerializer,
    CustomFieldValueSerializer,
    EndpointSerializer,
    HttpOperatorConnectionModelSerializer,
    WorkflowModelSerializer,
)

# Custom Field API Views
class CustomFieldListCreateView(generics.ListCreateAPIView):
    queryset = CustomField.objects.all()
    serializer_class = CustomFieldSerializer

class CustomFieldRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomField.objects.all()
    serializer_class = CustomFieldSerializer

# Custom Field Value API Views
class CustomFieldValueListCreateView(generics.ListCreateAPIView):
    queryset = CustomFieldValue.objects.all()
    serializer_class = CustomFieldValueSerializer

class CustomFieldValueRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomFieldValue.objects.all()
    serializer_class = CustomFieldValueSerializer

# Endpoint API Views
class EndpointListCreateView(generics.ListCreateAPIView):
    queryset = Endpoint.objects.all()
    serializer_class = EndpointSerializer

class EndpointRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Endpoint.objects.all()
    serializer_class = EndpointSerializer

# Connection API Views
class ConnectionListCreateView(generics.ListCreateAPIView):
    queryset = HttpOperatorConnectionModel.objects.all()
    serializer_class = HttpOperatorConnectionModelSerializer

class ConnectionRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = HttpOperatorConnectionModel.objects.all()
    serializer_class = HttpOperatorConnectionModelSerializer

# Workflow API Views
class WorkflowListCreateView(generics.ListCreateAPIView):
    queryset = WorkflowModel.objects.all()
    serializer_class = WorkflowModelSerializer

class WorkflowRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = WorkflowModel.objects.all()
    serializer_class = WorkflowModelSerializer

# views.py
class MediaViewSet(viewsets.ModelViewSet):
    queryset = Media.objects.all()
    serializer_class = MediaSerializer

    @action(detail=True,methods=["post"],url_path="download-media")
    def download_media(self,request,pk=None):
        latest_available_scout = Scout.objects.latest('created_at')
        client = login_user(latest_available_scout)
        media_obj = self.get_object()
        try:
            media_id = client.media_pk_from_url(media_obj.media_url)
            media = client.media_info(media_id)
            media_obj.download_url = media.thumbnail_url
            media_obj.save()
            return Response({"success":True},status=status.HTTP_200_OK) 
        except Exception as e:
            return Response({"error":str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    


class CustomFieldCreateView(CreateView):
    model = CustomField
    form_class = CustomFieldForm
    template_name = 'workflows/custom_field_form.html'
    success_url = reverse_lazy('custom_field_list')  # Redirect after creation


class CustomFieldUpdateView(UpdateView):
    model = CustomField
    form_class = CustomFieldForm
    template_name = 'workflows/custom_field_form.html'
    success_url = reverse_lazy('custom_field_list')  # Redirect after creation

class CustomFieldDeleteView(DeleteView):
    model = CustomField
    template_name = 'workflows/custom_field_confirm_delete.html'
    success_url = reverse_lazy('custom_field_list')  # Redirect after deletion

class CustomFieldListView(ListView):
    model = CustomField
    template_name = 'workflows/custom_field_list.html'
    context_object_name = 'custom_fields'

class CustomFieldValueCreateView(CreateView):
    model = CustomFieldValue
    form_class = CustomFieldValueForm
    template_name = 'workflows/custom_field_value_form.html'
    success_url = reverse_lazy('custom_field_list')  # Redirect after creation

    def form_valid(self, form):
        # Associate the custom field value with an endpoint (or other model)
        endpoint_id = self.kwargs['endpoint_id']
        endpoint = Endpoint.objects.get(id=endpoint_id)
        form.instance.content_object = endpoint  # Link to the endpoint
        # Create a JSON-like dictionary for saving
        field_name = form.cleaned_data['field'].name  # Get the name of the selected custom field
        field_value = form.cleaned_data['value']      # Get the input value
        
        # Constructing a dictionary to save as JSON
        json_value = {field_name: field_value}
        
        # Save the constructed JSON object in the value field
        form.instance.value = json_value
        return super().form_valid(form)


class EndpointListView(ListView):
    model = Endpoint
    template_name = 'workflows/endpoint_list.html'  # Template for listing endpoints
    context_object_name = 'endpoints'  # Variable name for the template context

class EndpointCreateView(CreateView):
    model = Endpoint
    form_class = EndpointForm
    template_name = 'workflows/endpoint_form.html'  # Template for creating an endpoint
    success_url = reverse_lazy('endpoint_list')  # Redirect URL after successful creation

class EndpointUpdateView(UpdateView):
    model = Endpoint
    form_class = EndpointForm
    template_name = 'workflows/endpoint_form.html'  # Template for updating an endpoint
    success_url = reverse_lazy('endpoint_list')  # Redirect URL after successful update

class EndpointDeleteView(DeleteView):
    model = Endpoint
    template_name = 'workflows/endpoint_confirm_delete.html'  # Template for confirming deletion
    success_url = reverse_lazy('endpoint_list')  # Redirect URL after successful deletion

class ConnectionListView(ListView):
    model = HttpOperatorConnectionModel
    template_name = 'workflows/connection_list.html'
    context_object_name = 'connections'

class ConnectionCreateView(CreateView):
    model = HttpOperatorConnectionModel
    form_class = HttpOperatorConnectionForm
    template_name = 'workflows/connection_form.html'
    success_url = reverse_lazy('connection_list')
    
    def form_valid(self, form):
        # Save the connection data to the database first
        connection = form.save()

        # Prepare data for Airflow API
        connection_data = {
            "connection_id": connection.connection_id,
            "conn_type": connection.conn_type,
            "host": connection.host,
            "port": connection.port,
            "login": connection.login,
            "password": connection.password,
            # Add other connection details as needed
        }

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        # Replace with your actual Airflow base URL and credentials
        airflowcred = AirflowCreds.objects.latest('created_at')
        username = airflowcred.username
        password = airflowcred.password

        # Make a POST request to the Airflow API
        response = requests.post(
            f"{airflowcred.airflow_base_url}/api/v1/connections",
            data=json.dumps(connection_data),
            headers=headers,
            auth=HTTPBasicAuth(username, password),
        )

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            messages.success(self.request, "Connection successfully created in both Django and Airflow.")
        else:
            messages.error(self.request, f"Failed to create connection in Airflow: {response.text}")
        return super().form_valid(form)
    
class ConnectionUpdateView(UpdateView):
    model = HttpOperatorConnectionModel
    form_class = HttpOperatorConnectionForm
    template_name = 'workflows/connection_form.html'
    success_url = reverse_lazy('connection_list')

    def form_valid(self, form):
        # Save the connection data to the database first
        connection = form.save()

        # Prepare data for Airflow API
        connection_data = {
            "connection_id": connection.connection_id,
            "conn_type": connection.conn_type,
            "host": connection.host,
            "port": connection.port,
            "login": connection.login,
            "password": connection.password,
            # Add other connection details as needed
        }

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        # Replace with your actual Airflow base URL and credentials
        airflowcred = AirflowCreds.objects.latest('created_at')
        username = airflowcred.username
        password = airflowcred.password

        # Make a PATCH request to the Airflow API
        response = requests.patch(
            f"{airflowcred.airflow_base_url}/api/v1/connections/{self.object.connection_id}",
            data=json.dumps(connection_data),
            headers=headers,
            auth=HTTPBasicAuth(username, password),
        )

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            messages.success(self.request, "Connection successfully updated in both Django and Airflow.")
        else:
            messages.error(self.request, f"Failed to update connection in Airflow: {response.text}")

        return super().form_valid(form)

class ConnectionDeleteView(DeleteView):
    model = HttpOperatorConnectionModel
    template_name = 'workflows/connection_confirm_delete.html'
    success_url = reverse_lazy('connection_list')

    def form_valid(self, form):
        # Save the connection data to the database first
        
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        # Replace with your actual Airflow base URL and credentials
        airflowcred = AirflowCreds.objects.latest('created_at')
        username = airflowcred.username
        password = airflowcred.password

        # Make a DELETE request to the Airflow API
        response = requests.delete(
            f"{airflowcred.airflow_base_url}/api/v1/connections/{self.object.connection_id}",
            headers=headers,
            auth=HTTPBasicAuth(username, password),
        )

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            messages.success(self.request, "Connection successfully deleted in both Django and Airflow.")
        else:
            messages.error(self.request, f"Failed to delete connection in Airflow: {response.text}")

        return super().form_valid(form)

class WorkflowInline():
    form_class = WorkflowModelForm
    model = WorkflowModel
    template_name = "workflows/workflow.html"

    # @schema_context("lunyamwi")
    def form_valid(self, form, schema_name="lunyamwi"):
        with schema_context(schema_name):
            named_formsets = self.get_named_formsets()
            if not all((x.is_valid() for x in named_formsets.values())):
                return self.render_to_response(self.get_context_data(form=form))
            print(self.object,'---object')
            is_update = self.object is not None
            self.object = form.save()
            if is_update:
                dag = self.object.dagmodel_set.latest('created_at')
                try:
                    airflowcreds = AirflowCreds.objects.latest('created_at')
                    headers = {
                        "Content-Type": "application/json",
                        "Accept": "application/json",
                    }
                    dag_update_data = {
                        "is_paused": False
                    }
                    resp = requests.patch(f"{airflowcreds.airflow_base_url}/api/v1/dags/{dag.dag_id}", 
                                          data=json.dumps(dag_update_data),
                                          auth=HTTPBasicAuth(airflowcreds.username, airflowcreds.password),
                                          headers=headers)
                    if resp.status_code == 200:
                        messages.success(self.request, f"DAG updated successfully {resp.status_code}")
                    else:
                        messages.error(self.request, f"Failed to update DAG: {resp.status_code}-{resp.text}")
                except Exception as e:
                    messages.error(self.request, f"Failed to update DAG: {str(e)}")
                print("Updating workflow:", self.object)
                # Additional logic for updating can go here
            else:
                print("Creating new workflow:", self.object)
                # Additional logic for creation can go here


            # for every formset, attempt to find a specific formset save function
            # otherwise, just save.
            for name, formset in named_formsets.items():
                formset_save_func = getattr(self, 'formset_{0}_valid'.format(name), None)
                if formset_save_func is not None:
                    formset_save_func(formset)
                else:
                    formset.save()
            generate_dag_script(self.object)
        return redirect('list_workflows')

    def formset_dags_valid(self, formset):
        """
        Hook for custom formset saving.. useful if you have multiple formsets
        """
        dags = formset.save(commit=False)  # self.save_formset(formset, contact)
        # add this, if you have can_delete=True parameter set in inlineformset_factory func
        for obj in formset.deleted_objects:
            obj.delete()
        for dag in dags:
            dag.workflow = self.object
            dag.save()

    def formset_httpoperators_valid(self, formset):
        """
        Hook for custom formset saving.. useful if you have multiple formsets
        """
        httpoperators = formset.save(commit=False)  # self.save_formset(formset, contact)
        # add this, if you have can_delete=True parameter set in inlineformset_factory func
        for obj in formset.deleted_objects:
            obj.delete()
        for operator in httpoperators:
            operator.dag = self.object.dagmodel_set.latest('created_at')
            operator.save()


class WorkflowCreate(WorkflowInline, CreateView):

    def get_context_data(self, **kwargs):
        ctx = super(WorkflowCreate, self).get_context_data(**kwargs)
        ctx['named_formsets'] = self.get_named_formsets()
        return ctx

    def get_named_formsets(self):
        if self.request.method == "GET":
            return {
                'dags': DagFormSet(prefix='dags'),
                'httpoperators': SimpleHttpOperatorFormSet(prefix='httpoperators'),
            }
        else:
            return {
                'dags': DagFormSet(self.request.POST or None, self.request.FILES or None, prefix='dags'),
                'httpoperators': SimpleHttpOperatorFormSet(self.request.POST or None, self.request.FILES or None, prefix='httpoperators'),
            }
        

    
class WorkflowUpdate(WorkflowInline, UpdateView):

    def get_context_data(self, **kwargs):
        ctx = super(WorkflowUpdate, self).get_context_data(**kwargs)
        ctx['named_formsets'] = self.get_named_formsets()
        return ctx

    def get_named_formsets(self):
        return {
            'dags': DagFormSet(self.request.POST or None, self.request.FILES or None, instance=self.object, prefix='dags'),
            'httpoperators': SimpleHttpOperatorFormSet(self.request.POST or None, self.request.FILES or None, instance=self.object.dagmodel_set.latest('created_at'), prefix='httpoperators'),
        }
    



class WorkflowRunner(DetailView):
    model = WorkflowModel
    template_name = "workflows/workflow_runner.html"
    context_object_name = "workflow"
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['workflow'] = self.object
        context['dag'] = self.object.dagmodel_set.latest('created_at')
        # Add the form to the context
        context['form'] = WorkflowRunnerForm()
        return context

    def post(self, request, *args, **kwargs):
        workflow = self.get_object()
        dag_id = workflow.dagmodel_set.latest('created_at').dag_id

        # Create an instance of the form with the POST data
        form = WorkflowRunnerForm(request.POST)
        
        if form.is_valid():
            # Process the form data (e.g., execute the workflow)
            push_to = form.cleaned_data['push_to']
            # You can add logic here based on the value of push_to
            if push_to == 'gcp':
                try:
                    push_file_gcp(filename=dag_id)
                    messages.success(request, "DAG file pushed to GCP successfully.")
                except Exception as e:
                    messages.error(request, f"Failed to push DAG file to GCP: {str(e)}")
            elif push_to == 'ssh':
                try:
                    push_file(filename=dag_id)
                    messages.success(request, "DAG file pushed to SSH successfully.")
                except Exception as e:
                    messages.error(request, f"Failed to push DAG file to SSH: {str(e)}")
            
            # Redirect after processing
            return redirect('workflow_runner', pk=workflow.pk)
        
        # If the form is not valid, re-render the page with the form errors
        return self.render_to_response(self.get_context_data(form=form))
    

class TriggerRun(View):
    
    def get(self, request, *args, **kwargs):
        
        workflow = WorkflowModel.objects.get(id=kwargs['pk'])
        dag_id = workflow.dagmodel_set.latest('created_at').dag_id

        # Trigger the DAG run
        try:
            airflowcreds = AirflowCreds.objects.latest('created_at')
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
            dag_run_data = {'conf': {}, 'dag_run_id': f'{dag_id}_{str(uuid.uuid4())}', 'note': None}
            resp = requests.post(
                f"{airflowcreds.airflow_base_url}/api/v1/dags/{dag_id}/dagRuns",
                data=json.dumps(dag_run_data),
                auth=HTTPBasicAuth(airflowcreds.username, airflowcreds.password),
                headers=headers
            )
            if resp.status_code == 200:
                messages.success(request, "DAG run triggered successfully.")
            else:
                messages.error(request, f"Failed to trigger DAG run: {resp.text}")
        except Exception as e:
            messages.error(request, f"Failed to trigger DAG run: {str(e)}")
        
        return redirect('list_workflows')

def delete_httpoperator(request, pk):
    try:
        httpOperator = SimpleHttpOperatorModel.objects.get(id=pk)
    except httpOperator.DoesNotExist:
        messages.success(
            request, 'Object Does not exit'
            )
        return redirect('update_workflow', pk=httpOperator.dag.workflow.id)

    httpOperator.delete()
    messages.success(
            request, 'httpOperator deleted successfully'
            )
    return redirect('update_workflow', pk=httpOperator.dag.workflow.id)


def delete_dag(request, pk):
    try:
        dag = DagModel.objects.get(id=pk)
    except dag.DoesNotExist:
        messages.success(
            request, 'Object Does not exit'
            )
        return redirect('update_workflow', pk=dag.workflow.id)

    dag.delete()
    messages.success(
            request, 'dag deleted successfully'
            )
    return redirect('update_workflow', pk=dag.workflow.id)


class WorkflowList(ListView):
    model = WorkflowModel
    template_name = "workflows/workflows.html"
    context_object_name = "workflows"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['workflows'] = self.get_queryset()
        airflowcreds = AirflowCreds.objects.latest('created_at')
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        context['data'] = []
        try:
            print("Fetching DAGs from Airflow under construction")
            # resp = requests.get(f"{airflowcreds.airflow_base_url}/api/v1/dags", auth=HTTPBasicAuth(airflowcreds.username, airflowcreds.password),headers=headers)   
            # messages.success(self.request, "Fetched DAGs from Airflow successfully.")
            # if resp.status_code == 200:
            #     context['data'] = resp.json()
        except Exception as e:
            messages.error(self.request, f"Failed to fetch DAGs from Airflow: {str(e)}")

        # print(resp.json())
        return context




def display_workflows(request):
    workflows = WorkflowModel.objects.all()
    return render(request, 'workflows/workflows.html', {'workflows': workflows})



def generate_workflow(request):
    if request.method == 'POST':
        workflow_form = WorkflowModelForm(request.POST)
        simplehttpoperator_formset = SimpleHttpOperatorFormSet(request.POST)
        dag_formset = DagFormSet(request.POST)
        # import pdb;pdb.set_trace()
        if workflow_form.is_valid() and simplehttpoperator_formset.is_valid() and dag_formset.is_valid():
            workflow = workflow_form.save()
            simplehttpoperators = simplehttpoperator_formset.save()
            dags = dag_formset.save()
            workflow.simplehttpoperators.set(simplehttpoperators)
            for dag in dags:
                workflow.dag = dag  # WorkflowModel.dag is a foreign key
                workflow.save()
            generate_dag_script(workflow)
            return redirect("workflows")  # replace with your actual success page
        
    else:
        workflow_form = WorkflowModelForm()
        simplehttpoperator_formset = SimpleHttpOperatorFormSet(queryset=SimpleHttpOperatorModel.objects.none())
        dag_formset = DagFormSet(queryset=DagModel.objects.none())

    return render(request, 'workflows/workflow.html', {'workflow_form': workflow_form, 'simplehttpoperator_formset': simplehttpoperator_formset, 'dag_formset': dag_formset})


class PaginationClass(PageNumberPagination):
    page_size = 20  # Set the number of items per page
    page_size_query_param = 'page_size'
    max_page_size = 100




class InstagramLeadViewSet(viewsets.ModelViewSet):
    queryset = InstagramUser.objects.all()
    serializer_class = InstagramLeadSerializer
    pagination_class = PaginationClass

    @action(detail=False,methods=['post'],url_path='qualify-account')
    def qualify_account(self, request, pk=None):
        account = InstagramUser.objects.filter(username = request.data.get('username')).latest('created_at')
        accounts_qualified = []
        if account.info:
            account.qualified = request.data.get('qualify_flag')
            account.relevant_information = request.data.get("relevant_information")
            account.scraped = True
            account.save()
            accounts_qualified.append(
                {
                    "qualified":account.qualified,
                    "account_id":account.id
                }
            )
        else:
            return Response({"message":"user has not outsourced information"})
        
        return Response(accounts_qualified, status=status.HTTP_200_OK)

class ScoreViewSet(viewsets.ModelViewSet):
    queryset = Score.objects.all()
    serializer_class = ScoreSerializer

class QualificationAlgorithmViewSet(viewsets.ModelViewSet):
    queryset = QualificationAlgorithm.objects.all()
    serializer_class = QualificationAlgorithmSerializer

class SchedulerViewSet(viewsets.ModelViewSet):
    queryset = Scheduler.objects.all()
    serializer_class = SchedulerSerializer

class LeadSourceViewSet(viewsets.ModelViewSet):
    queryset = LeadSource.objects.all()
    serializer_class = LeadSourceSerializer


class SimpleHttpOperatorViewSet(viewsets.ModelViewSet):
    queryset = SimpleHttpOperatorModel.objects.all()
    serializer_class = SimpleHttpOperatorModelSerializer



class WorkflowViewSet(viewsets.ModelViewSet):
    queryset = WorkflowModel.objects.all()
    serializer_class = WorkflowModelSerializer
    pagination_class = PaginationClass

    
class ScrapFollowers(APIView):
    def post(self, request):
        username = request.data.get("username")
        delay = int(request.data.get("delay"))
        round_ =  int(request.data.get("round"))
        chain = request.data.get("chain")
        if isinstance(username,list):
            for account in username:
                if chain:
                    scrap_followers(account,delay,round_=round_)
                else:
                    scrap_followers.delay(account,delay,round_=round_)
        else:
            scrap_followers.delay(username,delay,round_=round_)
        return Response({"success":True},status=status.HTTP_200_OK)

class ScrapTheCut(APIView):

    def post(self,request):
        chain = request.data.get("chain")
        round_ = request.data.get("round")
        index = request.data.get("index")
        record = request.data.get("record", None)
        refresh = request.data.get("refresh", False)
        number_of_leads = request.data.get("number_of_leads",0)
        try:
            users = None
            if refresh:
                scrap_the_cut(round_number=round_)
            if refresh and record:
                scrap_the_cut(round_number=round_,record=record)
            if not record:
                users = ScrappedData.objects.filter(round_number=round_)[index:index+number_of_leads]
            else:
                users = ScrappedData.objects.filter(round_number=round_)

            if users.exists():
                if chain:
                    for user in users:
                        scrap_users(list(user.response.get("keywords")[1]),round_ = round_,index=index)
                else:
                    for user in users:
                        scrap_users.delay(list(user.response.get("keywords")[1]),round_ = round_,index=index)

                return Response({"success": True}, status=status.HTTP_200_OK)
            else:
                logging.warning("Unable to find user")
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ScrapStyleseat(APIView):

    def post(self,request):
        region = request.data.get("region")
        category = request.data.get("category")
        chain = request.data.get("chain")
        round_ = request.data.get("round")
        index = request.data.get("index")
        try:
            subprocess.run(["scrapy", "crawl", "styleseat","-a",f"region={region}","-a",f"category={category}"])
            users = ScrappedData.objects.filter(inference_key=region)
            if users.exists():
                if chain:
                    for user in users:
                        scrap_users(list(user.response.get("businessName")),round_ = round_,index=index)
                else:
                    for user in users:
                        scrap_users.delay(list(user.response.get("businessName")),round_ = round_,index=index)

                return Response({"success": True}, status=status.HTTP_200_OK)
            else:
                logging.warning("Unable to find user")
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ScrapGmaps(APIView):

    def post(self,request):
        search_string = request.data.get("search_string")
        chain = request.data.get("chain")
        round_ = request.data.get("round")
        index = request.data.get("index")
        try:
            subprocess.run(["scrapy", "crawl", "gmaps","-a",f"search_string={search_string}"])
            users = ScrappedData.objects.filter(inference_key=search_string)
            if users.exists():
                if chain:
                    for user in users:
                        scrap_users(list(user.response.get("business_name")),round_ = round_,index=index)
                else:
                    for user in users:
                        scrap_users.delay(list(user.response.get("business_name")),round_ = round_,index=index)

                return Response({"success": True}, status=status.HTTP_200_OK)
            else:
                logging.warning("Unable to find user")
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

class ScrapAPI(APIView):

    def get(self,request):
        try:
            # Execute Scrapy spider using the command line
            subprocess.run(["scrapy", "crawl", "api"])
            return Response({"success": True}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    


class ScrapSitemaps(APIView):

    def get(self,request):
        try:
            # Execute Scrapy spider using the command line
            subprocess.run(["scrapy", "crawl", "sitemaps"])
            return Response({"success": True}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

class ScrapMindBodyOnline(APIView):

    def post(self,request):
        chain = request.data.get("chain")
        try:
            if chain:
                scrap_mbo()
            else:    
                # Execute Scrapy spider using the command line
                scrap_mbo.delay()
            return Response({"success": True}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ScrapURL(APIView):

    def get(self,request):
        try:
            # Execute Scrapy spider using the command line
            subprocess.run(["scrapy", "crawl", "webcrawler"])
            return Response({"success": True}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class ScrapUsers(APIView):
    def post(self,request):
        query = request.data.get("query")
        round_ = int(request.data.get("round"))
        index = int(request.data.get("index"))
        chain = request.data.get("chain")

        if isinstance(query,list):
            if chain:
                scrap_users(query,round_ = round_,index=index)
            else:
                scrap_users.delay(query,round_ = round_,index=index)
            
        return Response({"success":True},status=status.HTTP_200_OK)



class ScrapInfo(APIView):
    def post(self,request):
        
        delay_before_requests = int(request.data.get("delay_before_requests",4))
        delay_after_requests = int(request.data.get("delay_after_requests",14))
        step = int(request.data.get("step",3))
        accounts = int(request.data.get("accounts",18))
        round_number = int(request.data.get("round",121))
        chain = request.data.get("chain",False)
        if chain:
            scrap_info(delay_before_requests,delay_after_requests,step,accounts,round_number)
        else:
            scrap_info.delay(delay_before_requests,delay_after_requests,step,accounts,round_number)
        return Response({"success":True},status=status.HTTP_200_OK)
    


class ScrapMedia(APIView):
    def post(self,request):
        media_links = request.data.get("media_links")
        chain = request.data.get("chain")
        if chain:
            scrap_media(media_links)
        else:
            scrap_media.delay(media_links)
        return Response({"success":True},status=status.HTTP_200_OK)



class InsertAndEnrich(APIView):
    def post(self,request):
        keywords_to_check = request.data.get("keywords_to_check")
        round_ = request.data.get("round")
        chain = request.data.get("chain")
        if chain:
            insert_and_enrich(keywords_to_check,round_)
        else:
            insert_and_enrich.delay(keywords_to_check,round_)
        return Response({"success":True},status=status.HTTP_200_OK)
    

class GetMediaIds(APIView):
    def post(self,request):
        round_ = request.data.get("round")
        chain = request.data.get("chain")
        
        datasets = []
        for user in InstagramUser.objects.filter(Q(round=round_) & Q(qualified=True)):
            resp = requests.post(f"https://api.{os.environ.get('DOMAIN1', '')}.boostedchat.com/v1/instagram/has-client-responded/",data={"username":user.username})
            print(resp.status_code)
            if resp.status_code == 200:
                if resp.json()['has_responded']:
                    return Response({"message":"No need to carry on further because client has responded"}, status=status.HTTP_200_OK)
            else:
                resp = requests.get(f"https://api.{os.environ.get('DOMAIN1', '')}.boostedchat.com/v1/instagram/account/retrieve-salesrep/{user.username}/")
                if resp.status_code == 200:
                    print(resp.json())
                    dataset = {
                        "mediaIds": user.info.get("media_id"),
                        "username_from": resp.json()['salesrep'].get('username','')
                    }
                    datasets.append(dataset)
            

        if chain and round_:  
            return Response({"data": datasets},status=status.HTTP_200_OK)
        else:
            return Response({"error":"There is an error fetching medias"}, status=400)
        

class GetMediaComments(APIView):
    def post(self,request):
        round_ = request.data.get("round")
        chain = request.data.get("chain")
        
        datasets = []
        for user in InstagramUser.objects.filter(Q(round=round_) & Q(qualified=True)):
            resp = requests.post(f"https://api.{os.environ.get('DOMAIN1', '')}.boostedchat.com/v1/instagram/has-client-responded/",data={"username":user.username})
            print(resp.status_code)
            if resp.status_code == 200:
                if resp.json()['has_responded']:
                    return Response({"message":"No need to carry on further because client has responded"}, status=status.HTTP_200_OK)
            else:
                resp = requests.get(f"https://api.{os.environ.get('DOMAIN1', '')}.boostedchat.com/v1/instagram/account/retrieve-salesrep/{user.username}/")
                if resp.status_code == 200:
                    print(resp.json())
                    dataset = {
                        "mediaId": user.info.get("media_id"),
                        "comment": user.info.get("media_comment"),
                        "username_from": resp.json()['salesrep'].get('username','')
                    }
                    datasets.append(dataset)

        
        
        if chain and round_:  
            return Response({"data": datasets},status=status.HTTP_200_OK)
        else:
            return Response({"error":"There is an error fetching medias"}, status=400)
        
class GetAccounts(APIView):
    def post(self,request):
        round_ = request.data.get("round")
        chain = request.data.get("chain")
        
        datasets = []
        for user in InstagramUser.objects.filter(Q(round=round_) & Q(qualified=True)):
            resp = requests.post(f"https://api.{os.environ.get('DOMAIN1', '')}.boostedchat.com/v1/instagram/has-client-responded/",data={"username":user.username})
            print(resp.status_code)
            if resp.status_code == 200:
                if resp.json()['has_responded']:
                    return Response({"message":"No need to carry on further because client has responded"}, status=status.HTTP_200_OK)
            else:
                resp = requests.get(f"https://api.{os.environ.get('DOMAIN1', '')}.boostedchat.com/v1/instagram/account/retrieve-salesrep/{user.username}/")
                if resp.status_code == 200:
                    print(resp.json())
                    dataset = {
                        "mediaId": user.info.get("media_id"),
                        "comment": user.info.get("media_comment"),
                        "usernames_to": user.info.get("username"),
                        "username": user.info.get("username"),
                        "username_from": resp.json()['salesrep'].get('username','')
                    }
                    datasets.append(dataset)
        
        
        if chain and round_:  
            return Response({"data": datasets},status=status.HTTP_200_OK)
        else:
            return Response({"error":"There is an error fetching medias"}, status=400)
        


class FetchPendingInbox(APIView):
    def post(self, request):
        inbox_dataset = fetch_pending_inbox(session_id=request.data.get("session_id"))
        return Response({"data":inbox_dataset},status=status.HTTP_200_OK)
    
class ApproveRequest(APIView):
    def post(self, request):
        approved_datasets = approve_inbox_requests(session_id=request.data.get("session_id"))
        return Response({"data":approved_datasets},status=status.HTTP_200_OK)

class SendDirectAnswer(APIView):
    def post(self, request):
        send_direct_answer(session_id=request.data.get("session_id"),
                           thread_id=request.data.get("thread_id"),
                           message=request.data.get("message"))
        return Response({"success":True},status=status.HTTP_200_OK)
    

class PayloadQualifyingAgent(APIView):
    def post(self, request):
        yesterday = timezone.now().date() - timezone.timedelta(days=1)
        yesterday_start = timezone.make_aware(timezone.datetime.combine(yesterday, timezone.datetime.min.time()))

        # Filter accounts that are qualified and created from yesterday onwards
        round_ = request.data.get("round",1209)
        scrapped_users = InstagramUser.objects.filter(
            Q(created_at__gte=yesterday_start)).distinct('username')

        payloads = []
        for user in scrapped_users:
            payload = {
                "department":"Qualifying Department",
                "Scraped":{
                    "username":user.username,
                    "relevant_information":user.info,
                    "Relevant Information":user.info,
                    "outsourced_info":user.info
                }
            }
            payloads.append(payload)
        return Response({"data":payloads}, status=status.HTTP_200_OK)


class PayloadScrappingAgent(APIView):
    def post(self, request):
        payloads = []
        payload = {
            "department":"Scraping Department",
            "Start":{
                "mediaId":"",
                "comment":"",
                "number_of_leads":1,
                "relevant_information":{
                    "dummy":"dummy"
                },
                "Relevant Information":{
                    "dummy":"dummy"
                },
                "outsourced_info":{"dummy":"dummy"}
            }
        }

        payloads.append(payload)
        return Response({"data":payloads}, status=status.HTTP_200_OK)


class PayloadAssignmentAgent(APIView):
    def post(self, request):
        round_ = request.data.get("round",1209)
        yesterday = timezone.now().date() - timezone.timedelta(days=1)
        yesterday_start = timezone.make_aware(timezone.datetime.combine(yesterday, timezone.datetime.min.time()))

        qualified_users = InstagramUser.objects.filter(
            Q(created_at__gte=yesterday_start) & Q(qualified=True))
        payloads = []
        for user in qualified_users:
            payload =  {
                "department":"Assignment Department",
                "Qualified":{
                    "username":user.username,
                    "salesrep_capacity":2,
                    "Influencer":"",
                    "outsourced_info":user.info,
                    "relevant_Information":user.relevant_information,
                    "Relevant Information":user.relevant_information,
                    "relevant_information":user.relevant_information
                }
            }
            payloads.append(payload)
        return Response({"data":payloads}, status=status.HTTP_200_OK)




class GeneratePasswordEnc(APIView):
    def post(self, request, *args, **kwargs):
        password = request.data.get("password")
        cl = Client()
        return Response({
            "enc_pass":cl.password_encrypt(password)
        })