// =============================================================
// Jenkinsfile – Employee Management System CI/CD Pipeline
// Declarative Pipeline – Windows Agent
// =============================================================
//
// REQUIRED SETUP (do this in Jenkins before running the pipeline):
//
//   1. Plugins to install (Manage Jenkins → Plugins → Available):
//        - Pipeline
//        - Git Plugin
//        - Docker Pipeline
//        - Credentials Binding
//        - JUnit
//        - Workspace Cleanup
//
//   2. Credentials (Manage Jenkins → Credentials → global → Add):
//        Kind        : Username with password
//        Username    : <your Docker Hub username>
//        Password    : <your Docker Hub password or access token>
//        ID          : DOCKERHUB_CREDENTIALS   ← exact value required
//
//   3. Environment variable (Manage Jenkins → System → Global Properties):
//        Name  : DOCKERHUB_USERNAME
//        Value : <your Docker Hub username>
//
// PIPELINE STAGES:
//   Checkout → Install Deps → Build → Tests → Docker Build → Docker Push → Deploy
//
// Tests MUST pass before Docker stages run.
// Docker Push is skipped automatically when credentials are not configured.
// =============================================================

pipeline {

    agent any

    environment {
        DOCKERHUB_USERNAME = "${env.DOCKERHUB_USERNAME ?: 'your-dockerhub-username'}"
        IMAGE_NAME         = "employee-management-system"
        IMAGE_TAG          = "${env.BUILD_NUMBER ?: 'latest'}"
        FULL_IMAGE         = "${DOCKERHUB_USERNAME}/${IMAGE_NAME}:${IMAGE_TAG}"
        LATEST_IMAGE       = "${DOCKERHUB_USERNAME}/${IMAGE_NAME}:latest"
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
                echo ">>> Checking out source code from GitHub..."
                checkout scm
                echo ">>> Build Number: ${env.BUILD_NUMBER}"
            }
        }

        // ------------------------------------------------------------------
        // Stage 2: Install Dependencies
        // ------------------------------------------------------------------
        stage('Install Dependencies') {
            steps {
                echo '>>> Installing Python dependencies...'
                bat '''
                    python -m venv venv
                    call venv\\Scripts\\activate.bat
                    python -m pip install --upgrade pip --quiet
                    pip install -r requirements.txt --quiet
                    echo Dependencies installed successfully.
                '''
            }
        }

        // ------------------------------------------------------------------
        // Stage 3: Build (syntax check)
        // ------------------------------------------------------------------
        stage('Build') {
            steps {
                echo '>>> Checking Python syntax...'
                bat '''
                    call venv\\Scripts\\activate.bat
                    python -m py_compile app.py
                    echo Syntax check passed.
                '''
            }
        }

        // ------------------------------------------------------------------
        // Stage 4: Automated Tests  ← pipeline stops here if any test fails
        // ------------------------------------------------------------------
        stage('Automated Tests') {
            steps {
                echo '>>> Running 13 automated tests with Pytest...'
                bat '''
                    call venv\\Scripts\\activate.bat
                    pytest test_app.py -v --tb=short --junitxml=test-results.xml
                '''
            }
            post {
                always {
                    junit allowEmptyResults: true, testResults: 'test-results.xml'
                }
                success {
                    echo '>>> All 13 tests PASSED – proceeding to Docker stages.'
                }
                failure {
                    echo '>>> Tests FAILED – pipeline stopped. Fix failing tests first.'
                }
            }
        }

        // ------------------------------------------------------------------
        // Stage 5: Docker Build
        // ------------------------------------------------------------------
        stage('Docker Build') {
            steps {
                echo ">>> Building Docker image: ${FULL_IMAGE}"
                bat """
                    docker build -t ${FULL_IMAGE} .
                    docker tag ${FULL_IMAGE} ${LATEST_IMAGE}
                    echo Docker image built successfully.
                """
            }
        }

        // ------------------------------------------------------------------
        // Stage 6: Docker Push  ← skipped when credentials not configured
        // ------------------------------------------------------------------
        stage('Docker Push') {
            when {
                expression {
                    try {
                        withCredentials([usernamePassword(
                            credentialsId: 'DOCKERHUB_CREDENTIALS',
                            usernameVariable: 'U',
                            passwordVariable: 'P')]) { return true }
                    } catch (e) {
                        echo "DOCKERHUB_CREDENTIALS not configured – skipping push."
                        return false
                    }
                }
            }
            steps {
                echo ">>> Pushing image to Docker Hub..."
                withCredentials([
                    usernamePassword(
                        credentialsId: 'DOCKERHUB_CREDENTIALS',
                        usernameVariable: 'DOCKER_USER',
                        passwordVariable: 'DOCKER_PASS'
                    )
                ]) {
                    bat """
                        echo %DOCKER_PASS%| docker login -u %DOCKER_USER% --password-stdin
                        docker push ${FULL_IMAGE}
                        docker push ${LATEST_IMAGE}
                        docker logout
                        echo Image pushed successfully.
                    """
                }
            }
        }

        // ------------------------------------------------------------------
        // Stage 7: Deploy
        // ------------------------------------------------------------------
        stage('Deploy') {
            steps {
                echo '>>> Deploying with Docker Compose...'
                bat '''
                    docker-compose down --remove-orphans || exit 0
                    docker-compose up -d --build
                    docker-compose ps
                '''
                echo ">>> Deployment complete."
                echo ">>>   App       : http://localhost:5000"
                echo ">>>   Prometheus: http://localhost:9090"
                echo ">>>   Grafana   : http://localhost:3000"
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
            echo '=== PIPELINE FAILED – check the stage that turned red ==='
        }
        always {
            bat 'docker image prune -f || exit 0'
            cleanWs()
        }
    }
}
