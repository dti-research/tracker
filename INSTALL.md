# Installing Tracker

```bash
pip3 install dti-tracker
```

## From source

We recommend that you either use virtualenv or Docker.

```bash
# Install Tracker Dependencies
sudo apt update
sudo apt install git make python3-pip

# Install Tracker
git clone https://github.com/dti-research/tracker
cd tracker
sudo -H pip3 install -e .

# Enable bash autocompletion for Tracker on boot
echo ""  >> ~/.bashrc
echo "# Bash autocompletion for Tracker"  >> ~/.bashrc
echo 'eval "$(_TRACKER_COMPLETE=source tracker)"'  >> ~/.bashrc
source ~/.bashrc
```

### For contributors

Install developer dependencies

```bash
pip install -r requirements-dev.txt
```
After that install the pre-commit hooks

```bash
pre-commit install
```

# Installing NVIDIA Drivers

```bash
# Add PPA
sudo add-apt-repository ppa:graphics-drivers
sudo apt update

# Install the driver that fits your GPU
sudo apt install nvidia-driver-XXX

# Verify installation after reboot
nvidia-smi
```
