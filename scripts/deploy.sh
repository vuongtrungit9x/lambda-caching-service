#!/bin/bash

# Check if the name is provided example my-first-analytic-service
if [ -z "$1" ]; then
  echo "Error: Missing arguments."
  echo "Usage: $0 <name>"
  exit 1
fi

NAME=$1

# Ensure S3 bucket exists for Lambda Code upload
cd ../terraform
terraform init
echo "token = \"${{ secrets.TOKEN }}\"" >> terraform.tfvars
echo "adobe_api_key = \"${{ secrets.ADOBE_API_KEY }}\"" >> terraform.tfvars
terraform apply -auto-approve --var="name=$NAME" -target=aws_s3_bucket.cache_lambda_s3

# Prepare Lambda Code
cd ../scripts
./lambda_zip.sh
./lambda_upload.sh $NAME-cache-lambda ap-southeast-1

# Deploy Terraform
cd ../terraform
terraform apply -auto-approve --var="name=$NAME"
