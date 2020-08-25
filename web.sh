#!/bin/bash

gunicorn crawler_jus.app:create_app --bind=0.0.0.0:5000 --workers=4