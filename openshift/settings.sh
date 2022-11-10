export PROJECT_NAMESPACE=${PROJECT_NAMESPACE:-exp-port-e-courriel}
export GIT_URI=${GIT_URI:-"https://github.com/CQEN-QDCE/indy-email-verification.git"}
export GIT_REF=${GIT_REF:-"features/quebec-email-verif"}
# The templates that should not have their GIT referances(uri and ref) over-ridden
# Templates NOT in this list will have they GIT referances over-ridden
# with the values of GIT_URI and GIT_REF
export skip_git_overrides="visual-verifier-build.yaml"