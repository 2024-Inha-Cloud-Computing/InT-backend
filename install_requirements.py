import subprocess

def install_package(package):
    try:
        subprocess.check_call(["pip", "install", package])
    except subprocess.CalledProcessError:
        print(f"Failed to install {package}, skipping.")

with open("requirements.txt", "r") as f:
    packages = f.readlines()

for package in packages:
    install_package(package.strip())
