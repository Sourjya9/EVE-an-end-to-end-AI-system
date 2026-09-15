# OpenTofu Infrastructure as Code for Eve

This directory contains OpenTofu (open-source Terraform alternative) configuration files for provisioning AWS infrastructure for Eve.

## Resources Provisioned
1. **Networking (VPC)**: Isolated VPC with public and private subnets across 2 Availability Zones.
2. **Database (RDS)**: AWS RDS PostgreSQL 16 instance with automated storage scaling and private subnet isolation.
3. **Compute (ECS Fargate)**: Serverless container execution for FastAPI backend.
4. **Monitoring (CloudWatch)**: Structured logging log groups and 5xx metric alarms.
5. **Security**: Least-privilege IAM roles and layered security groups.

## Quickstart
```bash
tofu init
tofu plan -var="db_password=SecurePassword123!"
tofu apply -var="db_password=SecurePassword123!"
```
