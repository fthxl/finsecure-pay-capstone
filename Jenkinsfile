pipeline {
    agent any

    environment {
        // ---- Change these if your values differ ----
        DOCKER_HUB_USER = 'fthx1'
        IMAGE_NAME      = 'finsecure-pay'
        GCP_PROJECT     = 'project-e9594590-c73e-43ed-9a4'
        GKE_CLUSTER     = 'finsecure-cluster'
        GKE_REGION      = 'asia-southeast1'
        // --------------------------------------------
        FULL_IMAGE      = "${DOCKER_HUB_USER}/${IMAGE_NAME}:${BUILD_NUMBER}"
    }

    stages {

        stage('Checkout') {
            steps {
                echo "Pulling source code from GitHub..."
                checkout scm
            }
        }

        stage('Test') {
            steps {
                echo "Running pytest in a fresh virtualenv..."
                sh '''
                    python3 -m venv .venv
                    . .venv/bin/activate
                    pip install --no-cache-dir -r requirements.txt
                    pytest -v
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                echo "Building image: ${FULL_IMAGE}"
                sh "docker build -t ${FULL_IMAGE} -t ${DOCKER_HUB_USER}/${IMAGE_NAME}:latest ."
            }
        }

        stage('Push to Docker Hub') {
            steps {
                echo "Pushing image to Docker Hub..."
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-creds',
                    usernameVariable: 'DH_USER',
                    passwordVariable: 'DH_PASS'
                )]) {
                    sh '''
                        echo "$DH_PASS" | docker login -u "$DH_USER" --password-stdin
                        docker push ${FULL_IMAGE}
                        docker push ${DOCKER_HUB_USER}/${IMAGE_NAME}:latest
                        docker logout
                    '''
                }
            }
        }

        stage('Deploy to GKE') {
            steps {
                echo "Deploying image ${FULL_IMAGE} to GKE..."
                withCredentials([file(
                    credentialsId: 'gcp-service-account-key',
                    variable: 'GCP_KEY_FILE'
                )]) {
                    sh '''
                        gcloud auth activate-service-account --key-file="$GCP_KEY_FILE"
                        gcloud config set project ${GCP_PROJECT}
                        gcloud container clusters get-credentials ${GKE_CLUSTER} \
                            --region ${GKE_REGION} \
                            --project ${GCP_PROJECT}
                        kubectl set image deployment/finsecure-deployment \
                            finsecure-container=${FULL_IMAGE} \
                            --record
                        kubectl rollout status deployment/finsecure-deployment --timeout=180s
                    '''
                }
            }
        }

        stage('Verify') {
            steps {
                echo "Verifying deployment..."
                withCredentials([file(
                    credentialsId: 'gcp-service-account-key',
                    variable: 'GCP_KEY_FILE'
                )]) {
                    sh '''
                        kubectl get pods -l app=finsecure-pay
                        kubectl get service finsecure-service
                    '''
                }
            }
        }
    }

    post {
        success {
            echo "Pipeline SUCCESS. Image ${FULL_IMAGE} is live on GKE."
        }
        failure {
            echo "Pipeline FAILED. Check logs above."
        }
        always {
            echo "Cleaning up local docker images..."
            sh "docker rmi ${FULL_IMAGE} || true"
            sh "docker rmi ${DOCKER_HUB_USER}/${IMAGE_NAME}:latest || true"
        }
    }
}