pipeline {
    agent any

    environment {
        ARM_SUBSCRIPTION_ID = 'ba024c33-bcd0-4304-9f29-3bbcce04f297'
        ARM_CLIENT_ID       = credentials('azure-client-id')
        ARM_CLIENT_SECRET   = credentials('azure-client-secret')
        ARM_TENANT_ID       = credentials('azure-tenant-id')
        REPO_URL           = 'https://github.com/anandukrishnakl/Mini-URL-Shortener.git'
        BRANCH             = 'main'
    }

    stages {
        stage('Clone Repository') {
            steps {
                checkout([
                    $class: 'GitSCM',
                    branches: [[name: env.BRANCH]],
                    userRemoteConfigs: [[url: env.REPO_URL]]
                ])
                sh 'ls -la'  // Verify files were cloned
            }
        }

        stage('Terraform Init') {
            steps {
                dir('terraform') {  // Assuming Terraform files are in a subdirectory
                    sh 'terraform init -input=false'
                }
            }
        }

        stage('Terraform Plan') {
            steps {
                dir('terraform') {
                    sh 'terraform plan -out=tfplan'
                    archiveArtifacts artifacts: 'terraform/tfplan', fingerprint: true
                }
            }
        }

        stage('Manual Approval') {
            steps {
                timeout(time: 1, unit: 'HOURS') {
                    input message: 'Deploy to production?', ok: 'Confirm'
                }
            }
        }

        stage('Terraform Apply') {
            steps {
                dir('terraform') {
                    sh 'terraform apply -input=false -auto-approve tfplan'
                }
            }
        }

        stage('Deploy Application') {
            steps {
                script {
                    // Add your application deployment steps here
                    // For example, deploying to Azure App Service:
                    sh 'az webapp up --name mini-url-shortener --resource-group your-resource-group'
                }
            }
        }
    }

    post {
        always {
            echo 'Pipeline execution completed'
            cleanWs()  // Clean workspace
        }
        success {
            slackSend(color: 'good', message: "Pipeline SUCCESSFUL: ${env.JOB_NAME} #${env.BUILD_NUMBER}")
        }
        failure {
            slackSend(color: 'danger', message: "Pipeline FAILED: ${env.JOB_NAME} #${env.BUILD_NUMBER}")
        }
    }

    options {
        timeout(time: 2, unit: 'HOURS')
        disableConcurrentBuilds()
        buildDiscarder(logRotator(numToKeepStr: '5'))
    }
}