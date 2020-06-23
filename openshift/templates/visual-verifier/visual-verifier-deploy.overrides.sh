_includeFile=$(type -p overrides.inc)
if [ ! -z ${_includeFile} ]; then
  . ${_includeFile}
else
  _red='\033[0;31m'; _yellow='\033[1;33m'; _nc='\033[0m'; echo -e \\n"${_red}overrides.inc could not be found on the path.${_nc}\n${_yellow}Please ensure the openshift-developer-tools are installed on and registered on your path.${_nc}\n${_yellow}https://github.com/BCDevOps/openshift-developer-tools${_nc}"; exit 1;
fi

# ================================================================================================================
# Special deployment parameters needed for injecting a user supplied settings into the deployment configuration
# ----------------------------------------------------------------------------------------------------------------
if createOperation; then
  # Ask the user to supply the sensitive parameters ...
  readParameter "OIDC_RP_PROVIDER_ENDPOINT - Please provide the URL for your VC OIDC Identty Provider.  The value may not be blank:" OIDC_RP_PROVIDER_ENDPOINT "" "false"
  readParameter "OIDC_RP_CLIENT_ID - Please provide your OIDC Identty Provider client id. This value must match the client id in your Identity Provider.  The value may not be blank:" OIDC_RP_CLIENT_ID "" "false"
  readParameter "OIDC_RP_CLIENT_SECRET - Please provide your OIDC Identty Provider client secret. This value must match the client secret in your Identity Provider.  If left blank, a 32 character long base64 encoded value will be randomly generated using openssl:" OIDC_RP_CLIENT_SECRET $(generateKey 32) "false"
  readParameter "VC_AUTHN_PRES_REQ_CONF_ID - Please provide the presentation request configuration id to be used when authenticating.  The value may not be blank:" VC_AUTHN_PRES_REQ_CONF_ID "" "false"
  readParameter "OIDC_CLAIMS_REQUIRED - Please provide the list of claims to be checked by the verifier as a comma-separated list of values.    The value may not be blank:" OIDC_CLAIMS_REQUIRED "" "false"
else
  # Secrets are removed from the configurations during update operations ...
  printStatusMsg "Update operation detected ...\nSkipping the prompts for OIDC_RP_PROVIDER_ENDPOINT, OIDC_RP_CLIENT_ID, OIDC_RP_CLIENT_SECRET, VC_AUTHN_PRES_REQ_CONF_ID, and OIDC_CLAIMS_REQUIRED secrets ... \n"
  writeParameter "OIDC_RP_PROVIDER_ENDPOINT" "prompt_skipped" "false"
  writeParameter "OIDC_RP_CLIENT_ID" "prompt_skipped" "false"
  writeParameter "OIDC_RP_CLIENT_SECRET" "prompt_skipped" "false"
  writeParameter "VC_AUTHN_PRES_REQ_CONF_ID" "prompt_skipped" "false"
  writeParameter "OIDC_CLAIMS_REQUIRED" "prompt_skipped" "false"
fi

SPECIALDEPLOYPARMS="--param-file=${_overrideParamFile}"
echo ${SPECIALDEPLOYPARMS}