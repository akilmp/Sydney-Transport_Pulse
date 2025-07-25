terraform {
  required_version = ">= 1.0"
}

provider "aws" {
  region = var.region
}

module "s3" {
  source      = "./modules/s3"
  bucket_name = var.data_lake_bucket
}

module "msk" {
  source                 = "./modules/msk"
  cluster_name           = var.msk_cluster_name
  kafka_version          = var.kafka_version
  broker_instance_type   = var.broker_instance_type
  number_of_broker_nodes = var.number_of_broker_nodes
  subnet_ids             = var.subnet_ids
  security_group_ids     = var.security_group_ids
}

module "emr" {
  source           = "./modules/emr"
  application_name = var.emr_application_name
  release_label    = var.kafka_version
}

module "mwaa" {
  source             = "./modules/mwaa"
  env_name           = var.mwaa_env_name
  dag_s3_path        = var.mwaa_dag_s3_path
  execution_role_arn = var.mwaa_execution_role_arn
  network_subnet_ids = var.subnet_ids
  security_group_ids = var.security_group_ids
}
