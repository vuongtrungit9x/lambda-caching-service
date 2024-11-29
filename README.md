# lambda-caching-service
Simple Caching Service 



## Deploy

You can deploy changes to infrastructure & lambda code by merging your changes into either the `staging-env` or `production-env` branches.

The `staging-env` and `production-env` branches should be the only branches that contain terraform state files. This means that the `main` branch and any feature branches should not contain any of the following files/folders:

```
terraform.tfstate.d
.terraform.lock.hcl
terraform.tfstate
terraform.tfstate.backup
```

You can also clone this repo and follow the setup guide below to deploy changes manually.


### Deploy Requirements:
1. Terraform CLI
2. AWS CLI, configured with the appropriate access profile.


### Deploy manually

Run `./scripts/deploy.sh <env-name>`, this will automatically:
1. Zip & Upload the latest code in `lambda.py`
2. Deploy changes to infrastructure & the lambda code from step 1.

`<env-name>` is a name that uniquely identifies this deployment. It will be prepended to all AWS resource names. **Use only lowercase letters and hyphens "-" as seperators for resource names.**
  