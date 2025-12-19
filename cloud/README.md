# Cloud

## Overview

We will be using Google Cloud Firebase - which will allow us to easily link the device and the app.

A simple "realtime database" will allow the app to see the _actual_ door state and trigger the open/close. Similarly, the Raspberry Pico will be able to _publish_ the door state and listen to the open/close requests.

## Setup

### GCP Resources

We'll be using command line tools and checked in config as much as possible, which means using Terraform and gcloud. These utilities must be installed first.

I use Fedora Linux, so I installed the Hashicorp repo and the google repo (for google, install the el8 repo).

```
sudo dnf config-manager addrepo --from-repofile=https://rpm.releases.hashicorp.com/fedora/hashicorp.repo
sudo dnf install terraform
sudo tee -a /etc/yum.repos.d/google-cloud-sdk.repo << EOM
[google-cloud-sdk]
name=Google Cloud SDK
baseurl=https://packages.cloud.google.com/yum/repos/cloud-sdk-el8-x86_64
enabled=1
gpgcheck=1
repo_gpgcheck=0
gpgkey=https://packages.cloud.google.com/yum/doc/yum-key.gpg https://packages.cloud.google.com/yum/doc/rpm-package-key.gpg
EOM
sudo dnf install google-cloud-sdk
```

I'm pretty sure you'll need to create a firebase project using the Firebase console first, in order to accept terms and conditions. This can immediately be deleted.

Here are the commands to get things going once I got past that:

```
gcloud init
gcloud auth application-default login
terraform init
terraform apply -var="project_id=XXXXX"
```

If this works (I had to re-run it for some reason), it will spit out a "URL" for the Realtime Database. You'll need to grab this for one of the next steps.

### Firebase Database "Rules"

Best practice is to use the `firebase` tool, which is available in the `npm` ecosystem.

Tool installation:
```
sudo dnf install nodejs npm
sudo npm install -g firebase-tools
firebase --version
```

Tool use:
```
firebase login
firebase init
# Select Realtime Database and Hosting features
# Select your existing project you created above
# Accept the default, "public" for the directory
# Don't accept the default for a single-page app.
# Don't setup automatic builds using github
# Accept the default for the database.rules.json file
firebase deploy
``` 

After editing the rules, you must redeploy them:
```
firebase deploy --only database
```
