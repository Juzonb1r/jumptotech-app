pipeline {
  agent any

  environment {
    REGISTRY = "localhost:5001"
    IMAGE_PREFIX = "jumptotech"

    GITOPS_REPO   = "https://github.com/Juzonb1r/jumptotech-gitops.git"
    GITOPS_BRANCH = "main"
  }

  stages {
    stage('Checkout app repo') {
      steps {
        checkout scm
        sh 'git rev-parse --short HEAD > .gitsha'
        sh 'echo "GIT SHA: $(cat .gitsha)"'
      }
    }

    stage('Build images (parallel)') {
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
            def svc = s // important: closure fix
            builds[svc] = {
              sh """
                set -e
                echo "=== BUILD: ${svc} ==="
                docker build -t ${REGISTRY}/${IMAGE_PREFIX}/${svc}:${sha} ./services/${svc}
              """
            }
          }
          parallel builds
        }
      }
    }

    stage('Push images (sequential)') {
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

          for (s in services) {
            sh """
              set -e
              echo "=== PUSH: ${s} ==="
              docker push ${REGISTRY}/${IMAGE_PREFIX}/${s}:${sha}
            """
          }
        }
      }
    }

    stage('Update GitOps repo tags (dev)') {
      steps {
        script {
          def sha = readFile('.gitsha').trim()

          withCredentials([string(credentialsId: 'github-gitops-token', variable: 'GITHUB_TOKEN')]) {
            sh """
              set -e
              rm -rf gitops

              # clone using token (repo can be public, but push needs auth)
              git clone --branch ${GITOPS_BRANCH} https://x-access-token:${GITHUB_TOKEN}@github.com/Juzonb1r/jumptotech-gitops.git gitops

              cd gitops

              # IMPORTANT: set git identity for CI commits
              git config user.email "jenkins@jumptotech.local"
              git config user.name "Jenkins CI"

              for svc in auth-service courses-service enrollment-service content-service news-service gateway-service; do
                file="dev/values/\${svc}.yaml"
                echo "Updating \${file} tag -> ${sha}"
                sed -i.bak "s/^  tag: .*/  tag: \\"${sha}\\"/g" "\${file}"
                rm -f "\${file}.bak"
              done

              git status
              git add dev/values/*.yaml
              git commit -m "dev: bump images to ${sha}" || echo "No changes to commit"
              git push origin ${GITOPS_BRANCH}
            """
          }
        }
      }
    }

    stage('Verify Registry') {
      steps {
        sh '''
          echo "=== REGISTRY CATALOG ==="
          curl -s http://localhost:5001/v2/_catalog || true
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