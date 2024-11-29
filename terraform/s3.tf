resource "aws_s3_bucket" "cache_s3" {
  bucket = "${var.name}-cache"
}

resource "aws_s3_bucket" "cache_lambda_s3" {
  bucket = "${var.name}-cache-lambda"
}

resource "aws_s3_bucket_lifecycle_configuration" "file_expiration" {
  bucket = aws_s3_bucket.cache_s3.id

  rule {
    id     = "expire-objects-after-365-days"
    status = "Enabled"

    filter {
      prefix = "" # Apply the rule to all objects in the bucket
    }

    expiration {
      days = 365
    }
  }
}