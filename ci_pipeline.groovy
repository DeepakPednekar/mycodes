pipeline {
    environment {
        gitLabRepoUrl = ''
        gitLabBuildRepoUrl = ''
        repoRegistryUrl = ''
        deployFileName = ''
        k8sDeploymentName = ''
        buildFilesToCopy = ''
        //replicas = 10
        
    }
    agent { label 'docker-' }
    stages {                
        stage('Image build and push') {
            steps {
                withFolderProperties {
                    cleanWs()
                    script { 
                        def repoUrlArr = gitLabRepoUrl.tokenize('/')
                        env.repoDir = repoUrlArr[-1]
                        def buildRepoUrlArr = gitLabBuildRepoUrl.tokenize('/')
                        env.buildRepoDir = buildRepoUrlArr[-1]
                    } 
                    checkout([ 
                    $class: 'GitSCM', 
                    branches: [[name: gitRepoBranch]], 
                    doGenerateSubmoduleConfigurations: false, 
                    extensions: [[$class: 'RelativeTargetDirectory', relativeTargetDir: repoDir]], 
                    submoduleCfg: [], 
                    userRemoteConfigs: [[credentialsId: gitCredential, url: gitLabRepoUrl]]])

                    checkout([  
                    $class: 'GitSCM', 
                    branches: [[name: gitBuildBranch]], 
                    doGenerateSubmoduleConfigurations: false, 
                    extensions: [[$class: 'RelativeTargetDirectory', relativeTargetDir: buildRepoDir]], 
                    submoduleCfg: [], userRemoteConfigs: [[credentialsId: gitCredential, url: gitLabBuildRepoUrl]]])
                    script {
                        def repoRegistryUrl

                        dir(buildRepoDir) {
                            sh '''
                                for i in $buildFilesToCopy
                                    do cp $i ${WORKSPACE}/$repoDir
                                    done
                            '''
                        }       

                        dir(repoDir) {
                            downLoadFilebeatConfig (gitRepoBranch)                        

                            def tagName = gitRepoBranch + '-' + env.BUILD_ID
                            registryUrl = env.repoRegistryUrl + '/' + gitRepoBranch
                            imageBuildAndPush(registryUrl, tagName)
                            env.IMAGE_NAME = registryUrl + ':' + tagName
                                }
                        }
                }
            }
        } 
        stage('Deploy to k8s') {                
            steps {
                withFolderProperties {
                    script {
                        dir(repoDir) { 
                            downloadAndExecutek8sdeploy()
                        }        
                    }
                }
            }    
        }
    }
}

def downLoadFilebeatConfig (gitRepoBranch) {

    withCredentials([usernamePassword(credentialsId: gitCredential, passwordVariable: 'passwordVar', usernameVariable: '')]) {
        sh 'curl -o ./app.yml.template --fail --header "PRIVATE-TOKEN: \"${passwordVar}\"" "https://git.org/api/v4/projects/10/repository/files/app.yml.template/raw?ref=master"'
        }

    if (gitRepoBranch == 'staging') {
        withCredentials([usernamePassword(credentialsId: gitCredential, passwordVariable: 'passwordVar', usernameVariable: '')]) {
        sh 'curl -o ./filebeat.yml --fail --header "PRIVATE-TOKEN: \"${passwordVar}\"" "https://git.org/api/v4/projects/10/repository/files/filebeat%2Ffilebeat-staging.yml/raw?ref=master"'
        }
    }
    if (gitRepoBranch == 'master') {
        withCredentials([usernamePassword(credentialsId: gitCredential, passwordVariable: 'passwordVar', usernameVariable: '')]) {
        sh 'curl -o ./filebeat.yml --fail --header "PRIVATE-TOKEN: \"${passwordVar}\"" "https://git.org/api/v4/projects/10/repository/files/filebeat%2Ffilebeat-production.yml/raw?ref=master"'
        }
    }
}

def imageBuildAndPush (repoRegistryUrl, tagName) {
    env.REGISTRY_URL = repoRegistryUrl
    withDockerRegistry([url: 'https://$REGISTRY_URL']){
    def newImage = docker.build("$repoRegistryUrl:$tagName")
    newImage.push("$tagName")
    }
}

def downloadAndExecutek8sdeploy () {
    withCredentials([usernamePassword(credentialsId: gitCredential, passwordVariable: 'passwordVar', usernameVariable: '')]) {
        sh 'curl -o k8s_deploy.sh --fail --header "PRIVATE-TOKEN: \"${passwordVar}\"" "https://git.org/api/v4/projects/90/repository/files/k8s_deploy.sh/raw?ref=master"'
        }
        sh 'chmod +x ./k8s_deploy.sh && ./k8s_deploy.sh'
}