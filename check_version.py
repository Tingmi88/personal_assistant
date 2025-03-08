import pkg_resources

# Get version information for relevant packages
packages = [
    "llama-index",
    "llama-index-tools-google"
]

for package in packages:
    try:
        version = pkg_resources.get_distribution(package).version
        print(f"{package}: {version}")
    except pkg_resources.DistributionNotFound:
        print(f"{package}: Not installed") 