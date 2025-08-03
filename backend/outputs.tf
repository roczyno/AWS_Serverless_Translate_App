output "cognito_user_pool_id" {
  description = "Cognito User Pool ID"
  value       = aws_cognito_user_pool.main.id
}

output "cognito_user_pool_client_id" {
  description = "Cognito User Pool Client ID"
  value       = aws_cognito_user_pool_client.web_client.id
}

output "cognito_domain" {
  description = "Cognito Domain"
  value       = aws_cognito_user_pool_domain.main.domain
}

output "api_gateway_url" {
  description = "API Gateway URL"
  value       = "${aws_api_gateway_stage.main.invoke_url}"
}

output "api_gateway_endpoints" {
  description = "API Gateway endpoints"
  value = {
    translations = "${aws_api_gateway_stage.main.invoke_url}/translations"
    languages    = "${aws_api_gateway_stage.main.invoke_url}/languages"
  }
}