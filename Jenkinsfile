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
                echo "Pulling source code