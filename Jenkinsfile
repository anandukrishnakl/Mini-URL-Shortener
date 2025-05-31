pipeline {
    agent any

    environment {
        ARM_SUBSCRIPTION_ID = 'ba024c33-bcd0-4304-9f29-3bbcce04f297'
        ARM_CLIENT_ID       = credentials('azure-client-id')
        ARM_CLIENT_SECRET   = credentials('azure-client-secret')
        ARM_TENANT_ID       = credentials('azure-tenant-id')
        REPO_URL           = 'https://github.com/anandukrishnakl/Mini-URL-Shortener.git'
        BRANCH            = 'main'
        TERRAFORM_DIR      = 'terraform'  // Directory containing Terraform files
    }

    options {
        timeout(time: 1, unit: 'HOURS')
        disableConcurrentBuilds()
        buildDiscarder(logRotator(numToKeepStr: '5'))
    }

    stages {
        stage('Clone Repository') {
            steps {
                checkout([
                    $class: 'GitSCM',
                    branches: [[name: env.BRANCH]],
                    userRemoteConfigs: [[url: env.REPO_URL]],
                    extensions: [[$class: 'CleanBeforeCheckout']]
                )
                sh 'ls -la'  // Verify files were cloned
            }
        }

        stage('Terraform Init') {
            steps {
                dir(env.TERRAFORM_DIR) {
                    sh 'terraform init -input=false'
                }
            }
        }

        stage('Terraform Plan') {
            steps {
                dir(env.TERRAFORM_DIR) {
                    sh 'terraform plan -out=tfplan'
                    archiveArtifacts artifacts: 'tfplan', fingerprint: true
                }
            }
        }

        stage('Manual Approval') {
            steps {
                timeout(time: 15, unit: 'MINUTES') {
                    input message: 'Proceed with Terraform Apply?', ok: 'Deploy'
                }
            }
        }

        stage('Terraform Apply') {
            steps {
                dir(env.TERRAFORM_DIR) {
                    sh 'terraform apply -input=false -auto-approve tfplan'
                }
            }
        }

        stage('Deploy Application') {
            steps {
                script {
                    // Example: Deploy to Azure App Service
                    withCredentials([azureServicePrincipal(credentialsId: 'azure-credentials')]) {
                        sh '''
                        az login --service-principal -u $ARM_CLIENT_ID -p $ARM_CLIENT_SECRET --tenant $ARM_TENANT_ID
                        az account set --subscription $ARM_SUBSCRIPTION_ID
                        az webapp up --name mini-url-shortener --resource-group your-resource-group --runtime "PYTHON:3.9"
                        '''
                    }
                }
            }
        }
    }

    post {
        always {
            echo "Pipeline completed for ${env.JOB_NAME} #${env.BUILD_NUMBER}"
            cleanWs()  // Clean workspace
        }
        success {
            slackSend(color: 'good', message: "SUCCESS: ${env.JOB_NAME} deployed successfully!")
        }
        failure {
            slackSend(color: 'danger', message: "FAILED: ${env.JOB_NAME} build ${env.BUILD_NUMBER}")
            emailext (
                subject: "FAILED: ${env.JOB_NAME}",
                body: "Check console output at ${env.BUILD_URL}",
                to: 'devops@yourcompany.com'
            )
        }
    }
}