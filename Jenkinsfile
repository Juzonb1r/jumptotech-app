pipeline {
  agent any

  environment {
    REGISTRY = "localhost:5000"
    IMAGE_PREFIX = "jumptotech"
  }

  stages {
    stage('Checkout') {
      steps {
        checkout scm
        sh 'git rev-parse --short HEAD > .gitsha'
      }
    }

    stage('Build & Push (local registry)') {
      steps {
        script {
          def sha = readFile('.gitsha').trim()

          def services = [
            "auth-service",
            "courses-service",
            "enrollment-service",
            "content-service",
            "news-service",
            "gateway-service"
          ]

          def builds = [:]

          for (s in services) {
            def svc = s  // IMPORTANT: fix Groovy parallel closure bug
            builds[svc] = {
              sh """
                set -e
                echo "Building ${svc}..."
                docker build -t ${REGISTRY}/${IMAGE_PREFIX}/${svc}:${sha} ./services/${svc}
                docker push ${REGISTRY}/${IMAGE_PREFIX}/${svc}:${sha}
              """
            }
          }

          parallel builds
        }
      }
    }

    stage('Verify Registry') {
      steps {
        sh '''
          echo "Catalog:"
          curl -s http://localhost:5000/v2/_catalog || true
        '''
      }
    }
  }

  post {
    always {
      sh 'docker image prune -f || true'
    }
  }
}