#!/bin/bash

######################################################################
#                                                                    #
#    Script to download integration/test repository and pre-config   #
#    environment where tests are executed                            #
#                                                                    #
######################################################################

GIT_SERVER="git.opendaylight.org/gerrit/p"

echo "Wiping out workspace first."

rm -rf $WORKSPACE/*

echo "Setting up workspace"
if [ -d $WORKSPACE ]; then
  cd $WORKSPACE
else
  mkdir $WORKSPACE
  cd $WORKSPACE
fi

REPO="https://$GIT_SERVER/$GERRIT_PROJECT"
echo "Cloning repository $REPO"
git clone $REPO
# Enter into downloaded repository
cd `basename $GERRIT_PROJECT`

echo "Fetching upstream changes from $REPO"

git fetch --tags --progress $REPO $PATCHREFSPEC
COMMIT=`git rev-parse FETCH_HEAD^{commit}`
echo "Cheking out Revision $COMMIT"
git checkout -f $COMMIT

# Start environment configuration from WORKSPACE
cd $WORKSPACE
