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

output "amplify_app_id" {
  description = "AWS Amplify App ID"
  value       = aws_amplify_app.frontend.id
}

output "amplify_app_url" {
  description = "AWS Amplify App URL"
  value       = "https://${aws_amplify_branch.main.branch_name}.${aws_amplify_app.frontend.id}.amplifyapp.com"
}

output "amplify_branch_url" {
  description = "AWS Amplify Branch URL"
  value       = aws_amplify_branch.main.branch_name == "main" ? "https://${aws_amplify_app.frontend.id}.amplifyapp.com" : "https://${aws_amplify_branch.main.branch_name}.${aws_amplify_app.frontend.id}.amplifyapp.com"
}

output "frontend_url" {
  description = "Frontend application URL"
  value       = aws_amplify_branch.main.branch_name == "main" ? "https://${aws_amplify_app.frontend.id}.amplifyapp.com" : "https://${aws_amplify_branch.main.branch_name}.${aws_amplify_app.frontend.id}.amplifyapp.com"
}