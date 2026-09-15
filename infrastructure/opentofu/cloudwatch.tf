resource "aws_cloudwatch_log_group" "backend" {
  name              = "/ecs/eve-backend-${var.environment}"
  retention_in_days = 30
}

resource "aws_cloudwatch_metric_alarm" "backend_5xx" {
  alarm_name          = "eve-backend-5xx-alarm-${var.environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "HTTPCode_Target_5XX_Count"
  namespace           = "AWS/ApplicationELB"
  period              = 60
  statistic           = "Sum"
  threshold           = 5
  alarm_description   = "Triggers when backend API returns more than 5 5XX errors in one minute."
}
