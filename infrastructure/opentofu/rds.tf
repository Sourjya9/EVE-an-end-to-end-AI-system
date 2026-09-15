resource "aws_db_subnet_group" "rds" {
  name       = "eve-rds-subnet-group-${var.environment}"
  subnet_ids = [aws_subnet.private_a.id, aws_subnet.private_b.id]
  tags = {
    Name = "eve-rds-subnet-group"
  }
}

resource "aws_db_instance" "postgres" {
  identifier             = "eve-postgres-${var.environment}"
  allocated_storage      = 20
  max_allocated_storage  = 100
  engine                 = "postgres"
  engine_version         = "16.3"
  instance_class         = "db.t4g.micro"
  db_name                = "eve"
  username               = var.db_username
  password               = var.db_password
  db_subnet_group_name   = aws_db_subnet_group.rds.name
  vpc_security_group_ids = [aws_security_group.rds_sg.id]
  skip_final_snapshot    = true
  publicly_accessible    = false

  tags = {
    Name = "eve-rds-postgres"
  }
}
