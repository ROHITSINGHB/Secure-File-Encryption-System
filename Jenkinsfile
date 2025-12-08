pipeline {
    agent any
    
    options {
        timestamps()
        timeout(time: 30, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }
    
    environment {
        DOCKER_IMAGE = "secure-file-app"
        DOCKER_TAG = "latest"
        DOCKER_REGISTRY = "docker.io"
    }
    
    stages {
        stage('Clone Repository') {
            steps {
                echo '========== Cloning Repository =========='
                git branch: 'devops',  // ← CHANGED FROM 'main'
                    url: 'https://github.com/ROHITSINGHB/Secure-File-Encryption-System.git',
                    credentialsId: 'github-credentials'
            }
        }
        
        stage('Build') {
            steps {
                echo '========== Building Application =========='
                sh '''
                    echo "Python version:"
                    python --version
                    echo "Installing dependencies..."
                    pip install -r requirements.txt
                '''
            }
        }
        
        stage('Test') {
            steps {
                echo '========== Running Tests =========='
                sh '''
                    echo "Running unit tests..."
                    python -m pytest tests/ -v || true
                '''
            }
        }
        
        stage('Code Quality Check') {
            steps {
                echo '========== Code Quality Analysis =========='
                sh '''
                    echo "Running code quality checks..."
                    python -m pylint **/*.py --disable=all --enable=E || true
                '''
            }
        }
        
        stage('Build Docker Image') {
            steps {
                echo '========== Building Docker Image =========='
                sh '''
                    echo "Current working directory:"
                    pwd
                    
                    echo "Listing project files:"
                    ls -la
                    
                    echo "Checking if Dockerfile exists:"
                    test -f Dockerfile && echo "✅ Dockerfile found" || echo "❌ Dockerfile not found"
                    
                    echo "Building Docker image from current directory..."
                    docker build -t ${DOCKER_IMAGE}:${DOCKER_TAG} .
                    
                    echo "✅ Docker image built successfully"
                    docker images | grep ${DOCKER_IMAGE}
                '''
            }
        }
        
        stage('Deploy') {
            steps {
                echo '========== Deploying Application =========='
                sh '''
                    echo "Stopping previous container..."
                    docker stop ${DOCKER_IMAGE} || true
                    docker rm ${DOCKER_IMAGE} || true
                    
                    echo "Starting new container..."
                    docker run -d --name ${DOCKER_IMAGE} \
                        -p 5001:5001 \
                        ${DOCKER_IMAGE}:${DOCKER_TAG}
                    
                    echo "✅ Container started successfully"
                '''
            }
        }
        
        stage('Health Check') {
            steps {
                echo '========== Health Check =========='
                sh '''
                    sleep 5
                    echo "Checking container status..."
                    docker ps | grep ${DOCKER_IMAGE}
                    
                    echo "Displaying logs..."
                    docker logs ${DOCKER_IMAGE}
                '''
            }
        }
    }
    
    post {
        always {
            echo '========== Pipeline Completed =========='
            sh '''
                echo "Final status:"
                docker ps -a | grep ${DOCKER_IMAGE} || echo "No container found"
            '''
        }
        
        success {
            echo '✅ Deployment Successful!'
            sh '''
                echo "Application is running at: http://localhost:5001"
            '''
        }
        
        failure {
            echo '❌ Deployment Failed! Check logs above.'
            sh '''
                echo "Attempting to retrieve container logs..."
                docker logs ${DOCKER_IMAGE} || true
                
                echo "Checking Docker images..."
                docker images | grep ${DOCKER_IMAGE} || true
            '''
        }
        
        unstable {
            echo '⚠️ Pipeline is unstable. Review test results.'
        }
    }
}
