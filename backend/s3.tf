
resource "aws_s3_bucket" "document_input" {
  bucket = "${var.project_name}-input-${random_string.suffix.result}"
}

resource "aws_s3_bucket_versioning" "document_input" {
  bucket = aws_s3_bucket.document_input.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "document_input" {
  bucket = aws_s3_bucket.document_input.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "document_input" {
  bucket = aws_s3_bucket.document_input.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_cors_configuration" "document_input" {
  bucket = aws_s3_bucket.document_input.id

  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["GET", "PUT", "POST", "DELETE"]
    allowed_origins = var.allowed_origins
    expose_headers  = ["ETag"]
    max_age_seconds = 3000
  }
}


resource "aws_s3_bucket" "document_output" {
  bucket = "${var.project_name}-output-${random_string.suffix.result}"
}

resource "aws_s3_bucket_versioning" "document_output" {
  bucket = aws_s3_bucket.document_output.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "document_output" {
  bucket = aws_s3_bucket.document_output.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "document_output" {
  bucket = aws_s3_bucket.document_output.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
