version: 1
frontend:
  phases:
    preBuild:
      commands:
        - ls -la
        - cd Frontend
        - pwd
        - npm install
    build:
      commands:
        - ls -la
        - pwd
        - echo "Setting up environment variables"
        - echo "VITE_API_URL=${api_gateway_url}" >> .env.production
        - echo "VITE_COGNITO_USER_POOL_ID=${cognito_user_pool_id}" >> .env.production
        - echo "VITE_COGNITO_USER_POOL_CLIENT_ID=${cognito_user_pool_client_id}" >> .env.production
        - echo "VITE_COGNITO_DOMAIN=${cognito_domain}" >> .env.production
        - echo "VITE_REGION=${aws_region}" >> .env.production
        - npm run build
  artifacts:
    baseDirectory: Frontend/dist
    files:
      - '**/*'
  cache:
    paths:
      - Frontend/node_modules/**/* 