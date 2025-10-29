curl https://us-central1-apt.pkg.dev/doc/repo-signing-key.gpg | sudo apt-key add - && curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -

echo 'deb http://packages.cloud.google.com/apt apt-transport-artifact-registry-stable main' | sudo tee -a /etc/apt/sources.list.d/artifact-registry.list

sudo apt update

sudo apt install apt-transport-artifact-registry

gcloud beta artifacts print-settings apt --repository="gcp-exam-maker-repository" --location="us-central1" --project="guardadodiego"

echo "deb ar+https://us-central1-apt.pkg.dev/projects/guardadodiego gcp-exam-maker-repository main" | sudo tee -a /etc/apt/sources.list.d/artifact-registry.list

sudo apt update

sudo apt install gcp-exam-maker
