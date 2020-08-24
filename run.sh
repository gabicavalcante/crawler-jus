#!/bin/bash

process_number="0821901-51.2018.8.12.0001"

time scrapy runspider \
		--loglevel=INFO \
		tjcrawler/crawler/tjms_crawler.py \
		-a process_number="$process_number"