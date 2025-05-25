pipeline {
    agent any

    environment {
        ARM_SUBSCRIPTION_ID = 'ba024c33-bcd0-4304-9f29-3bbcce04f297'
        ARM_CLIENT_ID       = credentials('AZURE_CLIENT_ID')
        ARM_CLIENT_SECRET   = credentials('AZURE_CLIENT_SECRET')
        ARM_TENANT_ID       = credentials('AZURE_TENANT_ID')
    }

    stages {
        stage('Clone Repo') {
            steps {
                git 'https://github.com/anandukrishnakl/Mini-URL-Shortener.git'
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
