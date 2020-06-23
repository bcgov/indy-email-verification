# Description: Email Verification OIDC Demo App
export PROJECT_NAMESPACE="devex-von-image"
export GIT_URI="https://github.com/bcgov/vc-authn-oidc.git"
export GIT_REF="master"

export SKIP_PIPELINE_PROCESSING=1

export skip_git_overrides="visual-verifier-build.json"

export ignore_templates="indy-email-verification email-verification-agent-build email-verification-agent-deploy email-verification-service-build email-verification-service-deploy postgresql-build postgresql-deploy"

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# Override environments, since there is only one AT THE MOMENT:
# devex-von-image-tools
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
export TOOLS="devex-von-image-tools"
export DEPLOYMENT_ENV_NAME="tools"
export DEV="tools"
export TEST="tools"
export PROD="tools"
