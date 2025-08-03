
data "aws_region" "current" {}
data "aws_caller_identity" "current" {}


resource "aws_iam_role" "lambda_role" {
  name = "${var.project_name}-lambda-role-${random_string.suffix.result}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}


resource "aws_iam_role_policy" "lambda_policy" {
  name = "${var.project_name}-lambda-policy"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      },
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Resource = [
          "${aws_s3_bucket.document_input.arn}/*",
          "${aws_s3_bucket.document_output.arn}/*",
          aws_s3_bucket.document_input.arn,
          aws_s3_bucket.document_output.arn
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:UpdateItem",
          "dynamodb:DeleteItem",
          "dynamodb:Query",
          "dynamodb:Scan"
        ]
        Resource = [
          aws_dynamodb_table.translation_jobs.arn,
          "${aws_dynamodb_table.translation_jobs.arn}/index/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "translate:TranslateText",
          "translate:TranslateDocument"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "lambda:InvokeFunction"
        ]
        Resource = [
          "arn:aws:lambda:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:function:${var.project_name}-translation-worker-${random_string.suffix.result}"
        ]
      }
    ]
  })
}

data "archive_file" "api_handler" {
  type        = "zip"
  source_file = "${path.module}/api_handler.py"
  output_path = "${path.module}/api_handler.zip"
}

data "archive_file" "translation_worker" {
  type        = "zip"
  source_file = "${path.module}/translation_worker.py"
  output_path = "${path.module}/translation_worker.zip"
}

data "archive_file" "cors_handler" {
  type        = "zip"
  source_file = "${path.module}/cors_handler.py"
  output_path = "${path.module}/cors_handler.zip"
}


resource "aws_lambda_function" "api_handler" {
  filename         = data.archive_file.api_handler.output_path
  function_name    = "${var.project_name}-api-handler-${random_string.suffix.result}"
  role            = aws_iam_role.lambda_role.arn
  handler         = "api_handler.lambda_handler"
  runtime         = "python3.11"
  timeout         = 300 
  memory_size     = 512  

  environment {
    variables = {
      TRANSLATION_JOBS_TABLE = aws_dynamodb_table.translation_jobs.name
      INPUT_BUCKET          = aws_s3_bucket.document_input.bucket
      OUTPUT_BUCKET         = aws_s3_bucket.document_output.bucket
      COGNITO_USER_POOL_ID  = aws_cognito_user_pool.main.id
      TRANSLATION_WORKER_FUNCTION_NAME = aws_lambda_function.translation_worker.function_name
    }
  }

  depends_on = [
    aws_iam_role_policy.lambda_policy,
    aws_cloudwatch_log_group.api_handler_logs
  ]
}


resource "aws_lambda_function" "translation_worker" {
  filename         = data.archive_file.translation_worker.output_path
  function_name    = "${var.project_name}-translation-worker-${random_string.suffix.result}"
  role            = aws_iam_role.lambda_role.arn
  handler         = "translation_worker.lambda_handler"
  runtime         = "python3.11"
  timeout         = 300
  memory_size     = 512

  environment {
    variables = {
      TRANSLATION_JOBS_TABLE = aws_dynamodb_table.translation_jobs.name
      INPUT_BUCKET          = aws_s3_bucket.document_input.bucket
      OUTPUT_BUCKET         = aws_s3_bucket.document_output.bucket
    }
  }

  depends_on = [
    aws_iam_role_policy.lambda_policy,
    aws_cloudwatch_log_group.translation_worker_logs
  ]
}


resource "aws_lambda_function" "cors_handler" {
  filename         = data.archive_file.cors_handler.output_path
  function_name    = "${var.project_name}-cors-handler-${random_string.suffix.result}"
  role            = aws_iam_role.lambda_role.arn
  handler         = "cors_handler.lambda_handler"
  runtime         = "python3.11"
  timeout         = 30
  memory_size     = 128

  depends_on = [
    aws_iam_role_policy.lambda_policy,
    aws_cloudwatch_log_group.cors_handler_logs
  ]
}

resource "aws_cloudwatch_log_group" "api_handler_logs" {
  name              = "/aws/lambda/${var.project_name}-api-handler-${random_string.suffix.result}"
  retention_in_days = 14
}

resource "aws_cloudwatch_log_group" "translation_worker_logs" {
  name              = "/aws/lambda/${var.project_name}-translation-worker-${random_string.suffix.result}"
  retention_in_days = 14
}

resource "aws_cloudwatch_log_group" "cors_handler_logs" {
  name              = "/aws/lambda/${var.project_name}-cors-handler-${random_string.suffix.result}"
  retention_in_days = 14
}


resource "aws_s3_bucket_notification" "document_input_notification" {
  bucket = aws_s3_bucket.document_input.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.api_handler.arn
    events              = ["s3:ObjectCreated:*"]
    filter_suffix       = ".txt"
  }

  depends_on = [aws_lambda_permission.allow_s3_invoke]
}


resource "aws_lambda_permission" "allow_s3_invoke" {
  statement_id  = "AllowS3Invoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.api_handler.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.document_input.arn
}


resource "aws_lambda_permission" "allow_api_handler_invoke_translation_worker" {
  statement_id  = "AllowAPIHandlerInvokeTranslationWorker"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.translation_worker.function_name
  principal     = "lambda.amazonaws.com"
  source_arn    = aws_lambda_function.api_handler.arn
}