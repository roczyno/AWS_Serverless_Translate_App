version: 1
frontend:
  phases:
    preBuild:
      commands:
        - cd Frontend
        - npm install
    build:
      commands:
        - echo "Setting up environment variables"
        - echo "VITE_API_BASE_URLL=${api_gateway_url}" >> .env.production
        - echo "VITE_COGNITO_USER_POOL_ID=${cognito_user_pool_id}" >> .env.production
        - echo "VITE_COGNITO_CLIENT_ID=${cognito_user_pool_client_id}" >> .env.production
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
