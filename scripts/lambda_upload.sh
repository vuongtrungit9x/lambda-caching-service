#!/bin/bash

# Check if the bucket name and region are provided as arguments
if [ -z "$1" ] || [ -z "$2" ]; then
  echo "Error: Missing arguments."
  echo "Usage: $0 <bucket-name> <region>"
  exit 1
fi

BUCKET_NAME=$1
AWS_REGION=$2

aws s3 cp ../lambda.zip s3://$BUCKET_NAME/lambda.zip --region $AWS_REGION