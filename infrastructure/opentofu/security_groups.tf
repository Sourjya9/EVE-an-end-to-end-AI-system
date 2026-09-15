resource "aws_security_group" "alb_sg" {
  name        = "eve-alb-sg-${var.environment}"
  description = "Allows inbound HTTP to Application Load Balancer"
  vpc_id      = aws_vpc.main.id

  ingress {
    description = "HTTP Public"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "ecs_sg" {
  name        = "eve-ecs-sg-${var.environment}"
  description = "Allows traffic from ALB to ECS backend containers"
  vpc_id      = aws_vpc.main.id

  ingress {
    description     = "ALB to Backend API"
    from_port       = 8000
    to_port         = 8000
    protocol        = "tcp"
    security_groups = [aws_security_group.alb_sg.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "rds_sg" {
  name        = "eve-rds-sg-${var.environment}"
  description = "Allows Postgres traffic from ECS service"
  vpc_id      = aws_vpc.main.id

  ingress {
    description     = "ECS to PostgreSQL"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.ecs_sg.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
