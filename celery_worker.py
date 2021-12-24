#!/usr/bin/env python
import os
from celery import Celery
from flask import current_app
from configurator import Config

app = Celery('app')
app.config_from_object(Config, namespace='CELERY')
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
   print('Request: {0!r}'.format(self.request))
