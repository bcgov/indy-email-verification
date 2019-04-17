FROM bcgovimages/von-image:py36-1.8-2

USER root

# - In order to drop the root user, we have to make some directories writable
#   to the root group as OpenShift default security model is to run the container
#   under random UID.
RUN usermod -a -G 0 indy

USER indy

RUN pip3 install -e "git+https://github.com/nrempel/indy-catalyst.git@webhooks#egg=subdir&subdirectory=agent"