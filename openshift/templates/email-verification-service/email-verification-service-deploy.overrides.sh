#! /bin/bash
_includeFile=$(type -p overrides.inc)
# Import ocFunctions.inc for getSecret
_ocFunctions=$(type -p ocFunctions.inc)
if [ ! -z ${_includeFile} ]; then
  . ${_ocFunctions}
  . ${_includeFile}
else
  _red='\033[0;31m'; _yellow='\033[1;33m'; _nc='\033[0m'; echo -e \\n"${_red}overrides.inc could not be found on the path.${_nc}\n${_yellow}Please ensure the openshift-developer-tools are installed on and registered on your path.${_nc}\n${_yellow}https://github.com/BCDevOps/openshift-developer-tools${_nc}"; exit 1;
fi
# ===================================================================================
# Special Deployment Parameters needed for the email-verification-service instance.
# -----------------------------------------------------------------------------------
# ===================================================================================


if createOperation; then
  # Get the webhook URL
  readParameter "SMTP_EMAIL_HOST - Please provide the host name of the email server:" SMTP_EMAIL_HOST "smtp.host.io" "false"
  else
  # Secrets are removed from the configurations during update operations ...
  printStatusMsg "Getting SMTP_EMAIL_HOST for the ExternalNetwork definition from secret ...\n"
  writeParameter "SMTP_EMAIL_HOST" $(getSecret "${NAME}${SUFFIX}-email-host" "email-host") "false"
fi 

SPECIALDEPLOYPARMS="--param-file=${_overrideParamFile}"
echo ${SPECIALDEPLOYPARMS}

