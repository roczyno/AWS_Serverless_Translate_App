# AWS Serverless Document Translation Application

A modern, serverless document translation application built with AWS services, featuring a React frontend and automated infrastructure deployment.

## 🌟 Features

- **Multi-language Document Translation**: Support for various file formats including text files and PDFs
- **User Authentication**: Secure authentication using AWS Cognito
- **Real-time Translation Status**: Track translation progress with live updates
- **Drag & Drop File Upload**: Intuitive file upload interface
- **Responsive Design**: Modern UI built with React, TypeScript, and Tailwind CSS
- **Serverless Architecture**: Fully managed AWS services for scalability and cost-effectiveness
- **Automated Deployment**: One-click deployment with Terraform and AWS Amplify

## 🏗️ Architecture

### Frontend

- **React 18** with TypeScript for type safety
- **Vite** for fast development and building
- **Tailwind CSS** for modern, responsive styling
- **React Router** for client-side routing
- **AWS Amplify** for authentication and API integration
- **Lucide React** for beautiful icons

### Backend (AWS Serverless)

- **AWS Lambda** for serverless compute
- **Amazon Translate** for document translation
- **Amazon S3** for file storage (input and output buckets)
- **Amazon DynamoDB** for translation job tracking
- **Amazon API Gateway** for RESTful API endpoints
- **AWS Cognito** for user authentication and authorization
- **AWS Amplify** for frontend hosting and CI/CD

### Infrastructure

- **Terraform** for Infrastructure as Code (IaC)
- **Automated deployment scripts** for zero-touch deployment
- **GitHub integration** for continuous deployment

## 📁 Project Structure

```
AWS_Serveless_Translation/
├── backend/                          # Infrastructure and backend code
│   ├── lambda_functions/            # AWS Lambda functions
│   │   ├── api_handler.py           # API Gateway request handler
│   │   ├── cors_handler.py          # CORS configuration
│   │   └── translation_worker.py    # Document translation logic
│   ├── *.tf                         # Terraform configuration files
│   └── amplify-build.yml.tpl        # Amplify build template
├── Frontend/                        # React frontend application
│   ├── src/
│   │   ├── components/              # React components
│   │   │   ├── auth/               # Authentication components
│   │   │   ├── dashboard/          # Dashboard components
│   │   │   ├── upload/             # File upload components
│   │   │   └── translations/       # Translation management
│   │   ├── contexts/               # React contexts
│   │   ├── services/               # API services
│   │   └── types/                  # TypeScript type definitions
│   └── package.json                # Frontend dependencies
├── deploy_fully_automated.sh       # Automated deployment script
├── destroy_fully_automated.sh      # Infrastructure cleanup script
└── README.md                       # This file
```

## 🚀 Quick Start

### Prerequisites

- **AWS CLI** installed and configured with appropriate permissions
- **Terraform** (version >= 1.0) installed
- **Node.js** (version 16+) and npm
- **Git** for version control
- **GitHub account** with a repository for the project

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd AWS_Serveless_Translation
```

### 2. Configure GitHub Integration

Create a `backend/terraform.tfvars` file with your GitHub configuration:

```hcl
github_repo_url = "https://github.com/yourusername/your-repo-name"
github_access_token = "your-github-personal-access-token"
```

### 3. Deploy Infrastructure

Run the automated deployment script:

```bash
chmod +x deploy_fully_automated.sh
./deploy_fully_automated.sh
```

This script will:

- ✅ Initialize Terraform
- ✅ Deploy all AWS infrastructure
- ✅ Create Amplify app
- ✅ Connect to GitHub repository
- ✅ Configure build settings
- ✅ Trigger initial deployment

### 4. Access Your Application

After deployment, you'll receive:

- **Frontend URL**: Your live application
- **API Gateway URL**: Backend API endpoints
- **Cognito User Pool ID**: Authentication configuration

## 🛠️ Development

### Frontend Development

```bash
cd Frontend
npm install
npm run dev
```

The application will be available at `http://localhost:5173`

### Backend Development

The backend consists of AWS Lambda functions written in Python. To test locally:

1. Install AWS SAM CLI
2. Use AWS Lambda Test Events
3. Deploy changes using the deployment script

### Environment Variables

The application uses the following environment variables:

**Frontend (.env)**

```env
VITE_API_GATEWAY_URL=your-api-gateway-url
VITE_COGNITO_USER_POOL_ID=your-user-pool-id
VITE_COGNITO_USER_POOL_CLIENT_ID=your-client-id
VITE_AWS_REGION=us-east-1
```

**Backend (Lambda Environment Variables)**

```env
TRANSLATION_JOBS_TABLE=your-dynamodb-table
INPUT_BUCKET=your-input-s3-bucket
OUTPUT_BUCKET=your-output-s3-bucket
```

## 📖 Usage

### 1. User Registration/Login

- Visit the application URL
- Click "Get Started" to register or login
- Complete email verification (if required)

### 2. Upload Documents

- Navigate to the Dashboard
- Use the drag & drop interface or click to select files
- Choose source and target languages
- Click "Translate Document"

### 3. Monitor Progress

- View real-time translation status
- Track job progress in the dashboard
- Download translated documents when complete

### 4. Manage Translations

- View translation history
- Re-download previous translations
- Delete old translation jobs

## 🔧 Configuration

### Supported Languages

The application supports all languages available in Amazon Translate:

- **European Languages**: English, Spanish, French, German, Italian, Portuguese, etc.
- **Asian Languages**: Chinese, Japanese, Korean, Hindi, Thai, etc.
- **Middle Eastern Languages**: Arabic, Hebrew, Turkish, etc.
- **African Languages**: Swahili, Zulu, Afrikaans, etc.

### File Format Support

- **Text Files**: .txt, .doc, .docx
- **PDF Files**: .pdf (basic support)
- **Maximum File Size**: 10MB per file

### AWS Service Configuration

The infrastructure is configured with:

- **Lambda Timeout**: 5 minutes
- **S3 Bucket Lifecycle**: 30 days retention
- **DynamoDB TTL**: 90 days for job records
- **API Gateway Rate Limiting**: 1000 requests per second

## 🚨 Troubleshooting

### Common Issues

1. **Deployment Fails**

   - Verify AWS credentials are configured
   - Check GitHub token permissions
   - Ensure Terraform version compatibility

2. **Authentication Issues**

   - Verify Cognito User Pool configuration
   - Check CORS settings in API Gateway
   - Ensure frontend environment variables are set

3. **Translation Failures**
   - Check Lambda function logs in CloudWatch
   - Verify file format support
   - Ensure Amazon Translate service is enabled

### Debug Commands

```bash
# Check AWS credentials
aws sts get-caller-identity

# View Lambda logs
aws logs tail /aws/lambda/your-function-name

# Check DynamoDB table
aws dynamodb scan --table-name your-table-name

# Verify S3 bucket contents
aws s3 ls s3://your-bucket-name
```

## 🧹 Cleanup

To destroy the infrastructure and clean up resources:

```bash
chmod +x destroy_fully_automated.sh
./destroy_fully_automated.sh
```

**⚠️ Warning**: This will permanently delete all resources including:

- S3 buckets and their contents
- DynamoDB tables and data
- Lambda functions
- API Gateway endpoints
- Cognito User Pools
- Amplify applications

## 📊 Cost Optimization

### Estimated Monthly Costs (US East 1)

- **Lambda**: ~$5-20 (depending on usage)
- **S3**: ~$2-10 (storage and requests)
- **DynamoDB**: ~$5-15 (read/write capacity)
- **API Gateway**: ~$3-10 (requests)
- **Cognito**: ~$1-5 (MAUs)
- **Amplify**: ~$1 (hosting)

**Total**: ~$17-61/month for moderate usage

### Cost Optimization Tips

1. **S3 Lifecycle Policies**: Automatically delete old files
2. **DynamoDB TTL**: Remove old job records
3. **Lambda Concurrency**: Limit concurrent executions
4. **API Gateway Caching**: Reduce repeated API calls

## 🔒 Security

### Security Features

- **AWS Cognito**: Secure user authentication
- **IAM Roles**: Least privilege access
- **API Gateway**: Request validation and throttling
- **S3 Bucket Policies**: Secure file access
- **DynamoDB Encryption**: Data encryption at rest
- **VPC Configuration**: Network isolation (if needed)

### Best Practices

1. **Regular Security Updates**: Keep dependencies updated
2. **Access Monitoring**: Use AWS CloudTrail
3. **Secret Management**: Use AWS Secrets Manager for sensitive data
4. **Input Validation**: Validate all user inputs
5. **Error Handling**: Don't expose sensitive information in errors

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### Development Guidelines

- Follow TypeScript best practices
- Use meaningful commit messages
- Add tests for new features
- Update documentation as needed
- Follow AWS security best practices

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:

1. Check the troubleshooting section above
2. Review AWS documentation for specific services
3. Open an issue in the GitHub repository
4. Contact the development team

## 🔄 Version History

- **v1.0.0**: Initial release with basic translation functionality
- **v1.1.0**: Added PDF support and improved UI
- **v1.2.0**: Enhanced security and performance optimizations

---

**Built with ❤️ using AWS Serverless technologies**
