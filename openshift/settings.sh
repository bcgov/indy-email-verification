export PROJECT_NAMESPACE=${PROJECT_NAMESPACE}
export GIT_URI=${GIT_URI:-"https://github.com/bcgov/indy-email-verification.git"}
export GIT_REF=${GIT_REF:-"master"}

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# Override environments, since there is only one AT THE MOMENT:
# devex-von-image-tools
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
export TOOLS="4a9599-tools"
export DEPLOYMENT_ENV_NAME="dev"
export DEV="dev"
export TEST="test"
export PROD="prod"