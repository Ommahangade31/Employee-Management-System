// =============================================================
// Jenkinsfile – Employee Management System CI/CD Pipeline
// Declarative Pipeline
// =============================================================
//
// REQUIRED SETUP (do this in Jenkins before running the pipeline):
//
//   1. Plugins to install (Manage Jenkins → Plugins):
//        - Pipeline
//        - Git Plugin
//        - Docker Pipeline
//        - Credentials Binding
//        - JUnit (for test result graphs)
//        - Workspace Cleanup (for cleanWs())
//
//   2. Credentials to add (Manage Jenkins → Credentials → global → Add):
//        Kind            : Username with password
//        Username        : <your Docker Hub username>
//        Password        : <your Docker Hub password or access token>
//        ID              : DOCKERHUB_CREDENTIALS      ← exact value required
//        Description     : Docker Hub credentials
//
//   3. Jenkins environment variable (optional – or edit the default below):
//        Manage Jenkins → System → Global Properties → Environment Variables
//        Name  : DOCKERHUB_USERNAME
//        Value : <your Docker Hub username>
//
// PIPELINE STAGES:
//   Checkout → Install Deps → Build (syntax) → Tests → Docker Build → Docker Push → Deploy
//
// The pipeline STOPS if Tests fail. Docker Push only runs when the
// DOCKERHUB_CREDENTIALS credential exists.
// =============================================================

pipeline {

    agent any

    environment {
        // Set DOCKERHUB_USERNAME as a Jenkins env var, or replace the default here
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
                echo ">>> Checking out source code..."
                checkout scm
                sh 'echo "Commit: $(git rev-parse --short HEAD 2>/dev/null || echo unknown)"'
                echo ">>> Build : ${env.BUILD_NUMBER}"
            }
        }

        // ------------------------------------------------------------------
        // Stage 2: Install Dependencies
        // ------------------------------------------------------------------
        stage('Install Dependencies') {
            steps {
                echo '>>> Creating virtual environment and installing dependencies...'
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip --quiet
                    pip install -r requirements.txt --quiet
                    echo "Dependencies installed."
                '''
            }
        }

        // ------------------------------------------------------------------
        // Stage 3: Build (syntax check)
        // ------------------------------------------------------------------
        stage('Build') {
            steps {
                echo '>>> Checking Python syntax...'
                sh '''
                    . venv/bin/activate
                    python3 -m py_compile app.py
                    echo "Syntax OK."
                '''
            }
        }

        // ------------------------------------------------------------------
        // Stage 4: Automated Tests  ← pipeline stops here if tests fail
        // ------------------------------------------------------------------
        stage('Automated Tests') {
            steps {
                echo '>>> Running 13 automated tests with Pytest...'
                sh '''
                    . venv/bin/activate
                    pytest test_app.py -v --tb=short --junitxml=test-results.xml
                '''
            }
            post {
                always {
                    // Publish JUnit test results (requires JUnit plugin)
                    junit allowEmptyResults: true, testResults: 'test-results.xml'
                }
                success {
                    echo '>>> All tests PASSED – continuing to Docker stages.'
                }
                failure {
                    echo '>>> Tests FAILED – pipeline stopped. Fix the failing tests before retrying.'
                }
            }
        }

        // ------------------------------------------------------------------
        // Stage 5: Docker Build
        // ------------------------------------------------------------------
        stage('Docker Build') {
            steps {
                echo ">>> Building Docker image: ${FULL_IMAGE}"
                sh """
                    docker build -t ${FULL_IMAGE} .
                    docker tag ${FULL_IMAGE} ${LATEST_IMAGE}
                    echo "Image built: ${FULL_IMAGE}"
                """
            }
        }

        // ------------------------------------------------------------------
        // Stage 6: Docker Push  ← only runs when credential ID exists
        // ------------------------------------------------------------------
        stage('Docker Push') {
            when {
                // Only push when the credential has been configured in Jenkins
                expression {
                    try {
                        withCredentials([usernamePassword(
                            credentialsId: 'DOCKERHUB_CREDENTIALS',
                            usernameVariable: 'U', passwordVariable: 'P')]) { return true }
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
                    sh """
                        echo "\$DOCKER_PASS" | docker login -u "\$DOCKER_USER" --password-stdin
                        docker push ${FULL_IMAGE}
                        docker push ${LATEST_IMAGE}
                        docker logout
                        echo "Pushed: ${FULL_IMAGE}"
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
                sh '''
                    docker-compose down --remove-orphans || true
                    docker-compose up -d --build
                    docker-compose ps
                '''
                echo ">>> Deployed successfully."
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
            echo '=== PIPELINE FAILED – check the failed stage above ==='
        }
        always {
            // Remove dangling (untagged) Docker images to save disk space
            sh 'docker image prune -f || true'
            // Clean Jenkins workspace
            cleanWs()
        }
    }
}
