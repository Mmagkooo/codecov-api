import uuid

from django.db import models
from django.contrib.postgres.fields import JSONField, CITextField, ArrayField
from django.utils.functional import cached_property


class Version(models.Model):
    version = models.TextField(primary_key=True)

    class Meta:
        db_table = 'version'


class Repository(models.Model):
    repoid = models.AutoField(primary_key=True)
    name = CITextField()
    author = models.ForeignKey(
        'codecov_auth.Owner', db_column='ownerid', on_delete=models.CASCADE,)
    service_id = models.TextField()
    private = models.BooleanField()
    updatestamp = models.DateTimeField(auto_now=True)
    active = models.NullBooleanField()
    language = models.TextField(null=True, blank=True)
    fork = models.ForeignKey('core.Repository', db_column='forkid', on_delete=models.DO_NOTHING, null=True, blank=True)
    branch = models.TextField(null=True, blank=True)
    upload_token = models.UUIDField(default=uuid.uuid4)

    class Meta:
        db_table = 'repos'

    @property
    def service(self):
        return self.author.service

    @property
    def latest_commit(self):
        return Commit.objects.filter(repository=self.repoid).order_by('-timestamp').first()


class Branch(models.Model):
    name = models.TextField(primary_key=True, db_column='branch')
    repository = models.ForeignKey(
        'core.Repository', db_column='repoid', on_delete=models.CASCADE, related_name='branches')
    authors = ArrayField(models.IntegerField(
        null=True, blank=True), null=True, blank=True, db_column='authors')
    head = models.ForeignKey(
        'core.Commit', db_column='head', related_name='branch_head', on_delete=models.CASCADE,)
    updatestamp = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'branches'
    pass


class Commit(models.Model):
    commitid = models.TextField(primary_key=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    updatestamp = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(
        'codecov_auth.Owner', db_column='author', on_delete=models.CASCADE,)
    repository = models.ForeignKey(
        'core.Repository', db_column='repoid', on_delete=models.CASCADE, related_name='commits')
    ci_passed = models.BooleanField()
    totals = JSONField()
    report = JSONField()
    merged = models.NullBooleanField()
    deleted = models.NullBooleanField()
    notified = models.NullBooleanField()
    branch = models.TextField()
    pullid = models.IntegerField()
    message = models.TextField()
    parent_commit_id = models.TextField(db_column='parent')
    state = models.CharField(max_length=256)

    @cached_property
    def parent_commit(self):
        return Commit.objects.filter(repository=self.repository, commitid=self.parent_commit_id).first()

    class Meta:
        db_table = 'commits'
    pass


class Pull(models.Model):
    repository = models.ForeignKey(
        'core.Repository', db_column='repoid', on_delete=models.CASCADE, related_name='pull_requests')
    pullid = models.IntegerField(primary_key=True)
    issueid = models.IntegerField()
    state = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    base = models.ForeignKey('core.Commit', db_column='base',
                             related_name='pull_base', on_delete=models.CASCADE,)
    head = models.ForeignKey('core.Commit', db_column='head',
                             related_name='pull_head', on_delete=models.CASCADE,)
    compared_to = models.ForeignKey(
        'core.Commit', db_column='compared_to', related_name='compared_to', on_delete=models.CASCADE,)
    commentid = models.CharField(max_length=100)
    author = models.ForeignKey(
        'codecov_auth.Owner', db_column='author', on_delete=models.CASCADE,)
    updatestamp = models.DateTimeField(auto_now=True)
    diff = JSONField()
    flare = JSONField()

    class Meta:
        db_table = 'pulls'
    pass
