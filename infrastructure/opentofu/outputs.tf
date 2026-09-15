output "rds_endpoint" {
  description = "PostgreSQL database connection endpoint"
  value       = aws_db_instance.postgres.endpoint
}

output "cloudwatch_log_group" {
  description = "CloudWatch log group for backend container"
  value       = aws_cloudwatch_log_group.backend.name
}

output "ecs_cluster_name" {
  description = "ECS cluster name"
  value       = aws_ecs_cluster.main.name
}
