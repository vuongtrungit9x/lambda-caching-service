variable "name" {
  description = <<MULTI_LINE
  - A name that uniquely identifies this deployment.
  - It will be prepended to all AWS resource names. 
  - Many AWS resources enforce lowercase letters and widely support hyphens "-" as seperators for resource names.
  MULTI_LINE
  type        = string
}

variable "region" {
  description = "The aws region to use."
  type = string
  default = "ap-southeast-1"
}