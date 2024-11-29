output "lambda_arn" {
  value = aws_lambda_function.cache_lambda.arn
}

output "lambda_url" {
  value = aws_lambda_function_url.cache_url.function_url
}