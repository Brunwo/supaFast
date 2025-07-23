#!/bin/bash

export PROJECT_ID="durable-circle-455712-d3"  # change to your project ID
export REGION="europe-west1"

gcloud config set project "$PROJECT_ID"
gcloud config set compute/region "$REGION"
