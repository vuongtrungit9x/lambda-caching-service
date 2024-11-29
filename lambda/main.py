import boto3
import hashlib
import gzip
import json
import os

from handlers.ga4_handler import fetch_ga4_data
from handlers.gbq_handler import handle_gbq_request
from handlers.adobe_handler import handle_adobe_request
from handlers.pixel_handler import handle_pixel_request
from config_loader import load_config
from auth import authenticate_request

# Get the environment (default to 'stage')
env = os.getenv("ENV", "stage")
config = load_config(env)
S3_BUCKET_NAME = os.getenv("CACHE_BUCKET_NAME")
LAMBDA_FUNCTION_NAME = os.getenv("LAMBDA_FUNCTION_NAME")

# Initialize AWS clients
s3 = boto3.client("s3")
cloudwatch = boto3.client("cloudwatch")


def validate_env_vars():
    cache_s3_bucket_name = os.getenv("CACHE_BUCKET_NAME", None)
    if cache_s3_bucket_name is None:
        raise ValueError("Environment variable 'CACHE_BUCKET_NAME' is required.")

    lambda_function_name = os.getenv("LAMBDA_FUNCTION_NAME", None)
    if lambda_function_name is None:
        raise ValueError("Environment variable 'LAMBDA_FUNCTION_NAME' is required.")


def validate_request(body):
    """
    Validate the incoming request based on the provider and required fields.
    """
    required_top_fields = [
        "provider",
        "token",
        "startDate",
        "endDate",
        "searchCriteria",
    ]
    provider_specific_fields = {
        "GA4": ["property", "dimensions", "metrics", "offset", "limit", "orderBys"],
        "GBQ": ["propertyId", "dataset", "query"],
        "ADOBE": [
            "reportSuiteId",
            "metrics",
            "dimensions",
            "offset",
            "limit",
            "orderBys",
        ],
        "PIXEL": ["advertiserId", "parameters"],
    }

    # Check if top-level required fields are present
    for field in required_top_fields:
        if field not in body:
            raise ValueError(f"Missing required field: {field}")

    # Validate `provider`
    provider = body["provider"]
    if provider not in provider_specific_fields:
        raise ValueError(f"Unsupported provider: {provider}")

    # Check provider-specific fields
    missing_fields = [
        field
        for field in provider_specific_fields[provider]
        if field not in body["searchCriteria"]
    ]
    if missing_fields:
        raise ValueError(
            f"Missing {provider}-specific fields: {', '.join(missing_fields)}"
        )


def lambda_handler(event, context):
     # Authenticate request
    is_authenticated, error_message = authenticate_request(event, config)
    if not is_authenticated:
        return {
            "statusCode": 401,
            "body": f'{{"message": "{error_message}"}}'
        }

    validate_env_vars()
    try:
        # Parse the request body
        body = json.loads(event.get("body", "{}"))

        # Validate the request
        validate_request(body)

        cache_key = generate_cache_key(body)

        # Check S3 cache
        data = get_from_s3(cache_key)
        if data:
            log_cache_metric(True)

        else:
            # Fetch data from third-party API
            data = fetch_data_from_analytics_provider(body)
            put_to_s3(cache_key, data)
            log_cache_metric(False)
        # Return success response
        return {
            "statusCode": 200,
            "body": data
        }

    except Exception as e:
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}


def get_from_s3(key):
    try:
        response = s3.get_object(Bucket=S3_BUCKET_NAME, Key=key)
        compressed_data = response["Body"].read()
        data = gzip.decompress(compressed_data).decode("utf-8")
        return json.loads(data)
    except s3.exceptions.NoSuchKey:
        print(f"Cache miss for key: {key}")
        return None
    except Exception as e:
        print(f"Error fetching data from S3: {e}")
        raise e


def put_to_s3(key, data):
    try:
        compressed_data = gzip.compress(json.dumps(data).encode("utf-8"))
        s3.put_object(
            Bucket=S3_BUCKET_NAME, Key=key, Body=compressed_data, ContentEncoding="gzip"
        )
    except Exception as e:
        print(f"Error putting data to S3: {e}")
        raise e


def generate_cache_key(body):

    provider = body["provider"]
    search_criteria = body["searchCriteria"]

    if provider == "GA4":
        source_id = search_criteria["property"]
    elif provider == "GBQ":
        source_id = search_criteria["propertyId"]
    elif provider == "ADOBE":
        source_id = search_criteria["reportSuiteId"]
    elif provider == "PIXEL":
        source_id = search_criteria["advertiserId"]

    key_string = json.dumps(search_criteria)
    hash_request = hashlib.sha256(key_string.encode("utf-8")).hexdigest()
    return f"{provider}/{source_id}/{hash_request}"


def fetch_data_from_analytics_provider(body):

    provider = body["provider"]
    search_criteria = body["searchCriteria"]
    access_token = body["token"]

    # Route to appropriate handler based on provider
    if provider == "GA4":
        ga4_property_str = search_criteria["property"]
        ga4_property_id = ga4_property_str.split("/")[1]
        # handle_ga4_request(search_criteria)
        data = fetch_ga4_data(ga4_property_id, access_token, search_criteria)
    elif provider == "GBQ":
        data = handle_gbq_request(search_criteria)
    elif provider == "ADOBE":
        data = handle_adobe_request(search_criteria)
    elif provider == "PIXEL":
        data = handle_pixel_request(search_criteria)
    else:
        # This should not happen due to validation
        raise ValueError(f"Unsupported provider: {provider}")

    return data


def log_cache_metric(cache_hit):
    metric_name = "CacheHits" if cache_hit else "CacheMisses"
    try:
        cloudwatch.put_metric_data(
            Namespace="MyLambdaFunction",
            MetricData=[
                {
                    "MetricName": metric_name,
                    "Dimensions": [
                        {"Name": "FunctionName", "Value": LAMBDA_FUNCTION_NAME}
                    ],
                    "Unit": "Count",
                    "Value": 1,
                }
            ],
        )
    except Exception as e:
        print(f"Error logging metric to CloudWatch: {e}")
