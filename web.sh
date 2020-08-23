#!/bin/bash

gunicorn tjcrawler.api:app --bind=0.0.0.0:5000 --workers=4 --log-file -