# IAM Role for Lambda Execution
resource "aws_iam_role" "cache_execution_role" {
  name = "${var.name}-cache-lambda-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect    = "Allow",
        Principal = {
          Service = "lambda.amazonaws.com"
        },
        Action    = "sts:AssumeRole"
      }
    ]
  })
}

# Lambda Execution Policy
resource "aws_iam_role_policy" "lambda_policy" {
  name   = "${var.name}-cache-lambda-policy"
  role   = aws_iam_role.cache_execution_role.id
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "s3:ListBucket"
        ],
        Resource = "arn:aws:s3:::${aws_s3_bucket.cache_s3.id}"
      },
      {
        Effect = "Allow",
        Action = [
          "s3:GetObject",
          "s3:PutObject",
        ],
        Resource =  "arn:aws:s3:::${aws_s3_bucket.cache_s3.id}/*" 

      },
      {
        Effect   = "Allow",
        Action   = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
        ],
        Resource = "arn:aws:logs:*:*:*"
      },
      {
        Effect   = "Allow",
        Action   = [
          "cloudwatch:PutMetricData"
        ],
        Resource = "*"
      }
    ]
  })
}

# Lambda Function
resource "aws_lambda_function" "cache_lambda" {
  function_name = "${var.name}-cache-lambda"
  role          = aws_iam_role.cache_execution_role.arn
  handler       = "main.lambda_handler"
  runtime       = "python3.9"
  s3_bucket     = aws_s3_bucket.cache_lambda_s3.id
  s3_key        = "lambda.zip"
  source_code_hash = filebase64sha256("../lambda.zip")

  environment {
    variables = {
      CACHE_BUCKET_NAME = aws_s3_bucket.cache_s3.id
      LAMBDA_FUNCTION_NAME = "${var.name}-cache-lambda"
    }
  }
}


# Lambda Function URL
resource "aws_lambda_function_url" "cache_url" {
  function_name = aws_lambda_function.cache_lambda.function_name
  authorization_type = "NONE" # No authorization, URL is public
}

# Permissions to allow public access to Lambda URL
resource "aws_lambda_permission" "lambda_permission" {
  statement_id  = "AllowPublicAccess"
  action        = "lambda:InvokeFunctionUrl"
  principal     = "*"
  function_name = aws_lambda_function.cache_lambda.function_name
  function_url_auth_type = aws_lambda_function_url.cache_url.authorization_type
}