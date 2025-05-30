pipeline {
    agent any

    environment {
        ARM_SUBSCRIPTION_ID = 'ba024c33-bcd0-4304-9f29-3bbcce04f297'
        ARM_CLIENT_ID       = credentials('azure-client-id')
        ARM_CLIENT_SECRET   = credentials('azure-client-secret')
        ARM_TENANT_ID       = credentials('azure-tenant-id')
    }

    stages {
        stage('Clone Repo') {
            steps {
                git branch: 'main', url: 'https://github.com/anandukrishnakl/Mini-URL-Shortener.git'
            }
        }

        stage('Terraform Init') {
            steps {
                sh 'terraform init'
            }
        }

        stage('Terraform Plan') {
            steps {
                sh 'terraform plan'
            }
        }

        stage('Terraform Apply') {
            steps {
                input message: "Apply the changes?"
                sh 'terraform apply -auto-approve'
            }
        }
    }
}
