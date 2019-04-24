FROM bcgovimages/von-image:py36-1.8-3

USER root

# - In order to drop the root user, we have to make some directories writable
#   to the root group as OpenShift default security model is to run the container
#   under random UID.
RUN usermod -a -G 0 indy

RUN mkdir -p \
        $HOME/.indy_client/pool \
        $HOME/.indy_client/ledger-cache

# The root group needs access the directories under $HOME/.indy_client for the
# container to function in OpenShift.
RUN chown -R indy:root $HOME/.indy_client
RUN chmod -R ug+rw $HOME/log $HOME/ledger $HOME/.indy-cli $HOME/.indy_client

USER indy

RUN pip3 install -e "git+https://github.com/bcgov/indy-catalyst.git@master#egg=subdir&subdirectory=agent"
