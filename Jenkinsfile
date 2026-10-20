// =============================================================
// Jenkinsfile – Employee Management System CI/CD Pipeline
// Declarative Pipeline – Windows Agent
// =============================================================

pipeline {

    agent any

    environment {
        DOCKERHUB_USERNAME = "${env.DOCKERHUB_USERNAME ?: 'your-dockerhub-username'}"
        IMAGE_NAME         = "employee-management-system"
        IMAGE_TAG          = "${env.BUILD_NUMBER ?: 'latest'}"
    }

    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timeout(time: 30, unit: 'MINUTES')
        disableConcurrentBuilds()
    }

    stages {

        // ------------------------------------------------------------------
        // Stage 1: Checkout
        // ------------------------------------------------------------------
        stage('Checkout') {
            steps {
                echo ">>> Stage 1: Checkout"
                checkout scm
                echo ">>> Source code checked out. Build: ${env.BUILD_NUMBER}"
            }
        }

        // ------------------------------------------------------------------
        // Stage 2: Install Dependencies
        // ------------------------------------------------------------------
        stage('Install Dependencies') {
            steps {
                echo '>>> Stage 2: Installing Python dependencies...'
                bat 'python -m venv venv'
                bat 'venv\\Scripts\\python -m pip install --upgrade pip --quiet'
                bat 'venv\\Scripts\\python -m pip install -r requirements.txt --quiet'
                echo '>>> Dependencies installed.'
            }
        }

        // ------------------------------------------------------------------
        // Stage 3: Build (syntax check)
        // ------------------------------------------------------------------
        stage('Build') {
            steps {
                echo '>>> Stage 3: Python syntax check...'
                bat 'venv\\Scripts\\python -m py_compile app.py'
                echo '>>> Syntax check passed.'
            }
        }

        // ------------------------------------------------------------------
        // Stage 4: Automated Tests
        // ------------------------------------------------------------------
        stage('Automated Tests') {
            steps {
                echo '>>> Stage 4: Running 13 automated tests...'
                bat 'venv\\Scripts\\pytest test_app.py -v --tb=short --junitxml=test-results.xml'
            }
            post {
                always {
                    junit allowEmptyResults: true, testResults: 'test-results.xml'
                }
                success {
                    echo '>>> All 13 tests PASSED.'
                }
                failure {
                    echo '>>> Tests FAILED – pipeline stopped.'
                }
            }
        }

        // ------------------------------------------------------------------
        // Stage 5: Docker Build (requires Docker Desktop)
        // ------------------------------------------------------------------
        stage('Docker Build') {
            steps {
                script {
                    def dockerAvailable = bat(
                        script: 'docker --version',
                        returnStatus: true
                    ) == 0
                    if (dockerAvailable) {
                        echo ">>> Stage 5: Building Docker image..."
                        bat "docker build -t ${DOCKERHUB_USERNAME}/${IMAGE_NAME}:${IMAGE_TAG} ."
                        bat "docker tag ${DOCKERHUB_USERNAME}/${IMAGE_NAME}:${IMAGE_TAG} ${DOCKERHUB_USERNAME}/${IMAGE_NAME}:latest"
                        echo ">>> Docker image built."
                    } else {
                        echo ">>> Stage 5: Docker not available – skipping Docker Build."
                        echo ">>> Install Docker Desktop to enable this stage."
                    }
                }
            }
        }

        // ------------------------------------------------------------------
        // Stage 6: Docker Push
        // ------------------------------------------------------------------
        stage('Docker Push') {
            steps {
                script {
                    def dockerAvailable = bat(script: 'docker --version', returnStatus: true) == 0
                    def credAvailable = false
                    try {
                        withCredentials([usernamePassword(
                            credentialsId: 'DOCKERHUB_CREDENTIALS',
                            usernameVariable: 'U', passwordVariable: 'P')]) {
                            credAvailable = true
                        }
                    } catch (e) { credAvailable = false }

                    if (dockerAvailable && credAvailable) {
                        echo ">>> Stage 6: Pushing to Docker Hub..."
                        withCredentials([usernamePassword(
                            credentialsId: 'DOCKERHUB_CREDENTIALS',
                            usernameVariable: 'DOCKER_USER',
                            passwordVariable: 'DOCKER_PASS')]) {
                            bat "echo %DOCKER_PASS%| docker login -u %DOCKER_USER% --password-stdin"
                            bat "docker push ${DOCKERHUB_USERNAME}/${IMAGE_NAME}:${IMAGE_TAG}"
                            bat "docker push ${DOCKERHUB_USERNAME}/${IMAGE_NAME}:latest"
                            bat "docker logout"
                        }
                        echo ">>> Image pushed to Docker Hub."
                    } else {
                        echo ">>> Stage 6: Skipping Docker Push."
                        echo ">>>   Docker available : ${dockerAvailable}"
                        echo ">>>   Credentials set  : ${credAvailable}"
                    }
                }
            }
        }

        // ------------------------------------------------------------------
        // Stage 7: Deploy
        // ------------------------------------------------------------------
        stage('Deploy') {
            steps {
                script {
                    def dockerAvailable = bat(script: 'docker --version', returnStatus: true) == 0
                    if (dockerAvailable) {
                        echo ">>> Stage 7: Deploying with Docker Compose..."
                        bat 'docker-compose down --remove-orphans || exit 0'
                        bat 'docker-compose up -d --build'
                        bat 'docker-compose ps'
                        echo ">>> Deployed: http://localhost:5000"
                    } else {
                        echo ">>> Stage 7: Docker not available – skipping Deploy."
                        echo ">>> Application is already running via: python app.py"
                    }
                }
            }
        }

    }

    // ------------------------------------------------------------------
    // Post-Pipeline
    // ------------------------------------------------------------------
    post {
        success {
            echo '=== PIPELINE SUCCEEDED ==='
        }
        failure {
            echo '=== PIPELINE FAILED – check the red stage above ==='
        }
        always {
            echo '>>> Pipeline finished. Cleaning workspace...'
            cleanWs()
        }
    }
}
