#!/bin/bash

gcloud -q functions deploy json_and_rss_updater \
          --entry-point generate_json_and_rss \
          --max-instances 1 \
          --memory 128MB \
          --region europe-west2 \
          --runtime python37 \
          --service-account json-rss-updater-fn@worldfootballphonein-com.iam.gserviceaccount.com \
          --trigger-http
