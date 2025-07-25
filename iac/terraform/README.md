# Terraform Modules

This folder defines the AWS infrastructure used for the project. The code is organised into small modules so each service can be deployed independently or reused.

## Backend configuration

Terraform state is stored remotely using an S3 bucket and DynamoDB table for locking:

```hcl
terraform {
  backend "s3" {
    bucket         = "stp-tfstate"
    key            = "prod/terraform.tfstate"
    region         = "ap-southeast-2"
    dynamodb_table = "stp-tfstate-lock"
    encrypt        = true
  }
}
```

Initialise the backend with `terraform init`.

## Variables

The root module exposes a number of variables used by the modules:

| Name | Description | Default |
| ---- | ----------- | ------- |
| `region` | AWS region to deploy into | `ap-southeast-2` |
| `data_lake_bucket` | Name of the S3 bucket for the lake | n/a |
| `msk_cluster_name` | Name of the MSK cluster | n/a |
| `kafka_version` | Kafka version for MSK | `3.4.0` |
| `broker_instance_type` | Broker EC2 instance type | `kafka.m5.large` |
| `number_of_broker_nodes` | Number of MSK brokers | `2` |
| `subnet_ids` | Subnets used by MSK and MWAA | n/a |
| `security_group_ids` | Security groups applied to resources | n/a |
| `emr_application_name` | EMR Serverless application name | n/a |
| `mwaa_env_name` | Name of the MWAA environment | n/a |
| `mwaa_dag_s3_path` | S3 prefix where DAGs are stored | n/a |
| `mwaa_execution_role_arn` | IAM role ARN for MWAA | n/a |

Values can be provided via `terraform.tfvars` files for each environment.

## Module usage

Each service has its own module under `modules/`.

### S3

```hcl
module "s3" {
  source      = "./modules/s3"
  bucket_name = var.data_lake_bucket
}
```

### MSK

```hcl
module "msk" {
  source                 = "./modules/msk"
  cluster_name           = var.msk_cluster_name
  kafka_version          = var.kafka_version
  broker_instance_type   = var.broker_instance_type
  number_of_broker_nodes = var.number_of_broker_nodes
  subnet_ids             = var.subnet_ids
  security_group_ids     = var.security_group_ids
}
```

### EMR Serverless

```hcl
module "emr" {
  source           = "./modules/emr"
  application_name = var.emr_application_name
  release_label    = var.kafka_version
}
```

### MWAA

```hcl
module "mwaa" {
  source              = "./modules/mwaa"
  env_name            = var.mwaa_env_name
  dag_s3_path         = var.mwaa_dag_s3_path
  execution_role_arn  = var.mwaa_execution_role_arn
  network_subnet_ids  = var.subnet_ids
  security_group_ids  = var.security_group_ids
}
```

Run `terraform plan` to review the changes and `terraform apply` to create the infrastructure.
