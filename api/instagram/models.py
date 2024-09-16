from django.db import models
from api.helpers.models import BaseModel
from django.contrib.postgres.fields import ArrayField
from api.scout.models import Scout
import pytz

# Create your models here.
class Score(BaseModel):
    CRITERIA = (
        (0, 'none'),
        (1, 'type of keywords and number'),
        (2, 'number of times lead found during scrapping'),
        (3, 'negative points when disqualifying them'),
        (4, 'progress through sales funnel')
    )
    MEASURES = (
        (0, 'percentage'),
        (1, 'probability'),
        (2, 'linear scale')
    )
    name = models.CharField(max_length=255)
    criterion = models.IntegerField(choices=CRITERIA, default=0)
    measure = models.IntegerField(choices=MEASURES, default=0)
    linear_scale_capacity = models.IntegerField(blank=True, null=True)
    

class QualificationAlgorithm(BaseModel):
    name = models.CharField(max_length=255)
    positive_keywords = ArrayField(models.CharField(max_length=50), blank=True, null=True)
    number_positive_keywords = models.IntegerField()
    negative_keywords = ArrayField(models.CharField(max_length=50), blank=True, null=True)
    number_negative_keywords = models.IntegerField()
    score = models.ForeignKey(Score, on_delete=models.CASCADE, null=True, blank=True)


class Scheduler(BaseModel):
    TIMEZONE_CHOICES = [(tz, tz) for tz in pytz.all_timezones]
    name = models.CharField(max_length=255)
    timezone = models.CharField(max_length=63, choices=TIMEZONE_CHOICES, default='UTC')
    outreach_capacity = models.IntegerField()
    outreach_starttime = models.TimeField()
    outreach_endtime = models.TimeField()
    scrapper_starttime = models.DateTimeField()
    scrapper_endtime = models.DateTimeField(null=True,blank=True)



class LeadSource(BaseModel):
    CRITERIA = (
        (0, 'get similar accounts'),
        (1, 'get followers'),
        (2, 'get users'),
        (3, 'get posts with hashtag'),
        (4, 'interacted with photos'),
        (5, 'to be enriched from instagram'),
        (6, 'google maps'),
        (7, 'urls'),
        (8, 'apis')
    )
    name = models.CharField(max_length=255)
    criterion = models.IntegerField(choices=CRITERIA, default=0)
    account_usernames = ArrayField(models.CharField(max_length=50), blank=True, null=True)
    estimated_usernames = ArrayField(models.CharField(max_length=50), blank=True, null=True)
    photo_links = ArrayField(models.URLField(), blank=True, null=True)
    external_urls = ArrayField(models.URLField(), blank=True, null=True)
    hashtags = ArrayField(models.CharField(max_length=50), blank=True, null=True)
    google_maps_search_keywords = models.TextField(blank=True, null=True)
    enrich_with_url_in_bio = models.BooleanField(default=True)
    is_infinite_loop = models.BooleanField(default=True)



class InstagramUser(BaseModel):
    SOURCE_CHOICES = (
        (1, 'followers'),
        (2, 'searching_users'),
        (3, 'similar_accounts'),
    )
    username = models.CharField(max_length=255,null=True,blank=True)
    info = models.JSONField(null=True,blank=True)
    linked_to = models.CharField(max_length=50,null=True,blank=True)
    source = models.IntegerField(choices=SOURCE_CHOICES,default=1)
    round = models.IntegerField(null=True,blank=True)
    scout = models.ForeignKey(Scout,on_delete=models.CASCADE,null=True,blank=True)
    account_id = models.CharField(max_length=255,null=True,blank=True)
    account_id_pointer = models.BooleanField(default=False)
    outsourced_id = models.CharField(max_length=255,null=True,blank=True)
    outsourced_id_pointer = models.BooleanField(default=False)
    qualified_keywords = models.TextField(null=True, blank=True)
    qualified = models.BooleanField(default=False)
    scraped = models.BooleanField(default=False)
    relevant_information = models.JSONField(null=True,blank=True)
    influencer_source_key = models.CharField(max_length=255,null=True,blank=True)
    thread_id = models.CharField(max_length=255,null=True,blank=True)
    item_id = models.CharField(max_length=255,null=True,blank=True)
    user_id = models.CharField(max_length=255,null=True,blank=True)
    item_type = models.CharField(max_length=255,null=True,blank=True)
    timestamp = models.CharField(max_length=255,null=True,blank=True)
    cursor = models.TextField(null=True,blank=True)
    is_manually_triggered = models.BooleanField(default=False)
    

    def __str__(self) -> str:

        return self.username if self.username else 'cursor'



class DagModel(BaseModel):
    dag_id = models.CharField(max_length=255)
    description = models.TextField()
    schedule = models.CharField()
    schedule_interval = models.CharField(max_length=255)
    timetable = models.CharField(max_length=255,null=True,blank=True)
    start_date = models.DateTimeField(null=True,blank=True)
    end_date = models.DateTimeField(null=True,blank=True)
    full_filepath = models.CharField(max_length=255,null=True,blank=True)
    template_searchpath = models.CharField(null=True,blank=True)
    template_undefined = models.TextField(null=True,blank=True)
    user_defined_macros  = models.JSONField(null=True,blank=True)
    user_defined_filters = models.JSONField(null=True,blank=True)
    default_args = models.JSONField(null=True,blank=True)
    concurrency = models.IntegerField(null=True,blank=True)
    max_active_tasks = models.IntegerField(null=True,blank=True)
    max_active_runs = models.IntegerField(null=True,blank=True)
    dagrun_timeout = models.DateTimeField(null=True,blank=True)
    sla_miss_callback = models.TextField(null=True,blank=True)
    default_view = models.CharField(max_length=255,null=True,blank=True)
    orientation = models.CharField(max_length=255,null=True,blank=True)
    catchup = models.BooleanField(default=False)
    on_success_callback = models.TextField(null=True,blank=True)
    on_failure_callback = models.TextField(null=True,blank=True)
    doc_md = models.CharField(max_length=255,null=True,blank=True)
    params = models.JSONField(null=True,blank=True)
    access_control = models.JSONField(null=True,blank=True)
    is_paused_upon_creation = models.BooleanField(default=False)
    jinja_environment_kwargs = models.JSONField(null=True,blank=True)
    render_template_as_native_obj = models.BooleanField(default=False)
    tags = ArrayField(models.CharField(max_length=50), blank=True, null=True)
    owner_links = models.JSONField(null=True,blank=True)
    auto_register = models.BooleanField(default=False)
    fail_stop = models.BooleanField(default=False)
    trigger_url = models.URLField(null=True, blank=True)
    trigger_url_expected_response = models.TextField(null=True,blank=True)

    def __str__(self) -> str:
        return self.dag_id
    

class SimpleHttpOperatorModel(BaseModel):
    METHODS = (
        ("GET","GET"),
        ("POST","POST")
    )
    task_id = models.CharField(max_length=255,null=True, blank=True)
    http_conn_id=models.CharField(max_length=144,default="your_http_connection")
    endpoint = models.CharField(max_length=255)
    method = models.CharField(max_length=20, choices=METHODS, default="POST")
    data = models.JSONField(null=True,blank=True)
    headers = models.JSONField()
    response_check = models.CharField(max_length=1024,null=True,blank=True)
    extra_options = models.JSONField(null=True,blank=True)
    xcom_push = models.BooleanField(default=True)
    log_response = models.BooleanField(default=False)
    urls = ArrayField(models.JSONField(null=True, blank=True), blank=True, null=True)
    
    def __str__(self) -> str:
        return self.endpoint


class WorkflowModel(BaseModel):
    name = models.CharField(max_length=255,null=True, blank=True)
    simplehttpoperators = models.ManyToManyField(SimpleHttpOperatorModel)
    dag = models.ForeignKey(DagModel,on_delete=models.CASCADE,null=True, blank=True)
    delay_durations = models.JSONField(null=True,blank=True)
