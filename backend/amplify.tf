# AWS Amplify App for Frontend Deployment (Fully Automated)
resource "aws_amplify_app" "frontend" {
  name        = "${var.project_name}-frontend-${random_string.suffix.result}"
  description = "Frontend application for document translation service"
  
  # Direct Git integration - no manual connection needed
  repository   = var.github_repo_url
  access_token = var.github_access_token
  platform     = "WEB"
  
  # Enable automatic builds
  enable_branch_auto_build = true
  
  # Build settings for React/Vite app
  build_spec = templatefile("${path.module}/amplify-build.yml.tpl", {
    api_gateway_url = aws_api_gateway_stage.main.invoke_url
    cognito_user_pool_id = aws_cognito_user_pool.main.id
    cognito_user_pool_client_id = aws_cognito_user_pool_client.web_client.id
    cognito_domain = aws_cognito_user_pool_domain.main.domain
    aws_region = var.aws_region
  })

  # IAM service role for Amplify
  iam_service_role_arn = aws_iam_role.amplify_service_role.arn

  # Custom rules for SPA routing
  custom_rule {
    source = "/assets/<*>"
    target = "/assets/<*>"
    status = "200"
  }

  custom_rule {
    source = "/<*>"
    target = "/index.html"
    status = "200"
  }

  tags = {
    Name        = "${var.project_name}-amplify-app"
    Environment = var.environment
    Project     = var.project_name
  }
}

# Main branch for the Amplify app
resource "aws_amplify_branch" "main" {
  app_id            = aws_amplify_app.frontend.id
  branch_name       = "main"
  stage             = "DEVELOPMENT"
  enable_auto_build = true
  
  # Framework detection
  framework = "React"
  
  # Environment variables for the branch
  environment_variables = {
    VITE_API_URL = aws_api_gateway_stage.main.invoke_url
    VITE_COGNITO_USER_POOL_ID = aws_cognito_user_pool.main.id
    VITE_COGNITO_USER_POOL_CLIENT_ID = aws_cognito_user_pool_client.web_client.id
    VITE_COGNITO_DOMAIN = aws_cognito_user_pool_domain.main.domain
    VITE_REGION = var.aws_region
  }

  tags = {
    Name        = "${var.project_name}-main-branch"
    Environment = var.environment
    Project     = var.project_name
  }
}

# Automatic build trigger - no manual intervention needed
resource "terraform_data" "trigger_amplify_build" {
  depends_on = [aws_amplify_branch.main, aws_amplify_app.frontend]

  triggers_replace = {
    app_id      = aws_amplify_app.frontend.id
    branch_name = aws_amplify_branch.main.branch_name
    timestamp   = timestamp()
  }

  provisioner "local-exec" {
    command = "aws amplify start-job --app-id ${aws_amplify_app.frontend.id} --branch-name ${aws_amplify_branch.main.branch_name} --job-type RELEASE --region ${var.aws_region}"
  }
}

# S3 bucket for Amplify build artifacts
resource "aws_s3_bucket" "amplify_artifacts" {
  bucket = "${var.project_name}-amplify-artifacts-${random_string.suffix.result}"
  
  tags = {
    Name        = "${var.project_name}-amplify-artifacts"
    Environment = var.environment
    Project     = var.project_name
  }
}

# S3 bucket versioning
resource "aws_s3_bucket_versioning" "amplify_artifacts" {
  bucket = aws_s3_bucket.amplify_artifacts.id
  versioning_configuration {
    status = "Enabled"
  }
}

# S3 bucket public access block
resource "aws_s3_bucket_public_access_block" "amplify_artifacts" {
  bucket = aws_s3_bucket.amplify_artifacts.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# IAM role for Amplify service
resource "aws_iam_role" "amplify_service_role" {
  name = "${var.project_name}-amplify-service-role-${random_string.suffix.result}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "amplify.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name        = "${var.project_name}-amplify-service-role"
    Environment = var.environment
    Project     = var.project_name
  }
}

# IAM policy for Amplify service role
resource "aws_iam_role_policy" "amplify_service_policy" {
  name = "${var.project_name}-amplify-service-policy-${random_string.suffix.result}"
  role = aws_iam_role.amplify_service_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.amplify_artifacts.arn,
          "${aws_s3_bucket.amplify_artifacts.arn}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:${var.aws_region}:*:log-group:/aws/amplify/*"
      }
    ]
  })
} 