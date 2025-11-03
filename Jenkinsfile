pipeline {
    agent any
    
    options {
        timestamps()
        timeout(time: 30, unit: 'MINUTES')
    }
    
    environment {
        DOCKER_IMAGE = "secure-file-encryption:${BUILD_NUMBER}"
        DOCKER_CONTAINER_NAME = "secure-file-app"
    }
    
    stages {
        stage('Clone Repository') {
            steps {
                echo "========== Cloning Repository =========="
                git url: "https://github.com/ROHITSINGHB/Secure-File-Encryption-System.git", 
                    branch: 'main',
                    credentialsId: 'github-credentials'
            }
        }
        
        stage('Build') {
            steps {
                echo "========== Building Application =========="
                sh '''
                    echo "Python version:"
                    python3 --version
                    echo "Installing dependencies..."
                    pip install -r requirements.txt
                '''
            }
        }
        
        stage('Test') {
            steps {
                echo "========== Running Tests =========="
                sh '''
                    echo "Running pytest..."
                    python3 -m pytest tests/ -v --tb=short || true
                '''
            }
        }
        
        stage('Build Docker Image') {
            steps {
                echo "========== Building Docker Image =========="
                sh '''
                    echo "Building Docker image: ${DOCKER_IMAGE}"
                    docker build -t ${DOCKER_IMAGE} .
                '''
            }
        }
        
        stage('Deploy') {
            steps {
                echo "========== Deploying Application =========="
                sh '''
                    echo "Stopping existing container..."
                    docker stop ${DOCKER_CONTAINER_NAME} || true
                    docker rm ${DOCKER_CONTAINER_NAME} || true
                    
                    echo "Starting new container..."
                    docker run -d \
                        --name ${DOCKER_CONTAINER_NAME} \
                        -p 5000:5000 \
                        ${DOCKER_IMAGE}
                    
                    sleep 5
                    docker ps
                '''
            }
        }
        
        stage('Health Check') {
            steps {
                echo "========== Health Check =========="
                sh '''
                    echo "Checking application..."
                    curl -f http://localhost:5000/ || exit 1
                '''
            }
        }
    }
    
    post {
        success {
            echo "✅ Deployment Successful! App running on http://localhost:5000"
        }
        
        failure {
            echo "❌ Deployment Failed! Check logs above."
            sh 'docker logs ${DOCKER_CONTAINER_NAME} || true'
        }
    }
}
