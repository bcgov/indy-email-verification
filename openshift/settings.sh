export PROJECT_NAMESPACE=${PROJECT_NAMESPACE:-a99fd4}
export GIT_URI=${GIT_URI:-"https://github.com/bcgov/indy-email-verification.git"}
export GIT_REF=${GIT_REF:-"master"}
# The templates that should not have their GIT referances(uri and ref) over-ridden
# Templates NOT in this list will have they GIT referances over-ridden
# with the values of GIT_URI and GIT_REF
export skip_git_overrides="visual-verifier-build.yaml"