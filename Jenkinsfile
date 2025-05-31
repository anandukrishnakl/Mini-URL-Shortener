pipeline {
    agent any
    environment {
        // Azure Authentication
        ARM_SUBSCRIPTION_ID = 'ba024c33-bcd0-4304-9f29-3bbcce04f297'
        ARM_CLIENT_ID       = credentials('AZURE_CLIENT_ID')
        ARM_CLIENT_SECRET   = credentials('AZURE_CLIENT_SECRET')
        ARM_TENANT_ID       = credentials('AZURE_TENANT_ID')
        
        // Cosmos DB Configuration
        COSMOS_ENDPOINT     = 'https://cosmosdbaccountanandu.documents.azure.com:443/'
        COSMOS_KEY          = credentials('COSMOS_KEY')
        COSMOS_DATABASE     = 'urlshortenerdb'
        COSMOS_CONTAINER    = 'urls'
        
        // App Configuration
        APP_NAME            = 'webapp-urlshortener'
        RESOURCE_GROUP      = 'myResourceGroup'
        PYTHON_VERSION      = '3.9'
    }

    stages {
        stage('Checkout Code') {
            steps {
                checkout([
                    $class: 'GitSCM',
                    branches: [[name: 'main']],
                    extensions: [
                        [$class: 'CleanBeforeCheckout'],
                        [$class: 'RelativeTargetDirectory', relativeTargetDir: 'src']
                    ],
                    userRemoteConfigs: [[
                        url: 'https://github.com/anandukrishnakl/Mini-URL-Shortener.git',
                        credentialsId: 'github-token'
                    ]]
                ])
            }
        }

        stage('Verify Cosmos DB Connection') {
            steps {
                script {
                    try {
                        def response = sh(script: """
                            curl -s -X GET "$COSMOS_ENDPOINT" \\
                                 -H "x-ms-date: \$(date -u '+%a, %d %b %Y %H:%M:%S GMT')" \\
                                 -H "x-ms-version: 2018-12-31" \\
                                 -H "Authorization: \$(printf "$COSMOS_KEY" | base64)"
                        """, returnStdout: true)
                        
                        if (response.contains('"message":"unauthorized"')) {
                            error "Cosmos DB authentication failed"
                        } else {
                            echo "✅ Successfully connected to Cosmos DB"
                        }
                    } catch (Exception e) {
                        error "🚨 Cosmos DB connection failed: ${e.getMessage()}"
                    }
                }
            }
        }

        stage('Terraform Plan/Apply') {
            steps {
                dir('src/terraform') {
                    sh 'terraform init -input=false'
                    sh 'terraform validate'
                    sh 'terraform plan -out=tfplan'
                    input message: 'Approve Terraform Changes?'
                    sh 'terraform apply -input=false -auto-approve tfplan'
                }
            }
        }

        stage('Deploy Backend') {
            steps {
                dir('src/backend') {
                    sh "python -m pip install -r requirements.txt"
                    sh """
                    az webapp up \\
                        --name $APP_NAME \\
                        --resource-group $RESOURCE_GROUP \\
                        --runtime \"PYTHON|$PYTHON_VERSION\" \\
                        --logs
                    """
                    sh """
                    az webapp config appsettings set \\
                        --name $APP_NAME \\
                        --resource-group $RESOURCE_GROUP \\
                        --settings \\
                            COSMOS_ENDPOINT=$COSMOS_ENDPOINT \\
                            COSMOS_KEY=$COSMOS_KEY \\
                            COSMOS_DATABASE=$COSMOS_DATABASE \\
                            COSMOS_CONTAINER=$COSMOS_CONTAINER \\
                            ENVIRONMENT=production
                    """
                }
            }
        }

        stage('Smoke Test') {
            steps {
                script {
                    def healthCheck = sh(script: """
                        curl -s -o /dev/null -w '%{http_code}' \\
                        https://$APP_NAME.azurewebsites.net/health
                    """, returnStdout: true).trim()
                    
                    if (healthCheck != "200") {
                        error "Smoke test failed (HTTP $healthCheck)"
                    }
                }
            }
        }
    }

    post {
        always {
            // Cleanup processes
            bat '''
                taskkill /F /IM python.exe /T 2>nul || exit 0
                taskkill /F /IM uvicorn.exe /T 2>nul || exit 0
            '''
            cleanWs()
            
            // Archive Terraform state for audit
            archiveArtifacts artifacts: 'src/terraform/*.tfstate', allowEmptyArchive: true
        }
        
        success {
            slackSend(color: 'good', 
                message: """✅ *SUCCESS*: ${env.JOB_NAME} 
                • *Backend*: https://${APP_NAME}.azurewebsites.net
                • *Cosmos DB*: ${COSMOS_ENDPOINT}
                • *Build*: ${env.BUILD_URL}""")
        }
        
        failure {
            slackSend(color: 'danger',
                message: """❌ *FAILED*: ${env.JOB_NAME}
                • *Stage*: ${currentBuild.currentResult}
                • *Logs*: ${env.BUILD_URL}console""")
        }
    }

    options {
        timeout(time: 1, unit: 'HOURS')
        disableConcurrentBuilds()
        buildDiscarder(logRotator(numToKeepStr: '5'))
    }
}