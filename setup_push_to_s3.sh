#!/bin/bash
# Pycognaize Package S3 Push Script
# Prepares the Pycognaize package for local development and usage

set -e  # Exit immediately if a command exits with a non-zero status

# Parse command line arguments
DEV_MODE=false
UPLOAD_PACKAGE=false
while getopts "du" opt; do
    case $opt in
        d) DEV_MODE=true ;;
        u) UPLOAD_PACKAGE=true ;;
        *) echo "Usage: $0 [-d] [-u] (use -d for development mode, -u to upload package)" >&2
           exit 1 ;;
    esac
done

# Load environment variables from .env file if it exists
if [ -f ".env" ]; then
    echo "Loading environment variables from .env file..."
    set -a  # automatically export all variables
    source .env
    set +a
else
    echo "Warning: .env file not found. Environment variables may not be properly set."
fi

# Function to ask user if they want to increment version
ask_for_version_increment() {
    while true; do
        read -p "Do you want to increment the package version? (yes/no): " yn
        case $yn in
            [Yy]* ) return 0;;  # 0 for yes
            [Nn]* ) return 1;;  # 1 for no
            * ) echo "Please answer yes or no.";;
        esac
    done
}

# Function to get current version from pyproject.toml
get_current_version() {
    if [ ! -f "pyproject.toml" ]; then
        echo "Error: pyproject.toml not found!" >&2
        return 1
    fi
    current_version=$(grep -m 1 '^version = "' pyproject.toml | sed -e 's/version = "//' -e 's/"//')
    if [ -z "$current_version" ]; then
        echo "Error: Could not find version in pyproject.toml!" >&2
        return 1
    fi
    echo "$current_version"
    return 0
}

# Function to increment the patch version of a semantic version string
increment_patch_version() {
    local version=$1
    local major=$(echo "$version" | cut -d. -f1)
    local minor=$(echo "$version" | cut -d. -f2)
    local patch=$(echo "$version" | cut -d. -f3)

    if ! [[ "$major" =~ ^[0-9]+$ && "$minor" =~ ^[0-9]+$ && "$patch" =~ ^[0-9]+$ ]]; then
        echo "Error: Invalid version format for increment: $version" >&2
        return 1
    fi

    patch=$((patch + 1))
    echo "${major}.${minor}.${patch}"
    return 0
}

# Function to update the version in pyproject.toml
update_pyproject_version() {
    local new_version=$1
    local current_version
    current_version=$(get_current_version)
    if [ $? -ne 0 ]; then
        return 1 # Error already printed by get_current_version
    fi

    if [ ! -f "pyproject.toml" ]; then
        echo "Error: pyproject.toml not found!" >&2
        return 1
    fi

    # Ensure there is a version line to replace
    if ! grep -q -m 1 '^version = "' pyproject.toml; then
        echo "Error: Could not find version line in pyproject.toml to update." >&2
        return 1
    fi

    # Using a temporary file for sed to avoid issues with in-place editing on different OS
    sed "s/^version = \"${current_version}\"/version = \"${new_version}\"/" pyproject.toml > pyproject.toml.tmp && mv pyproject.toml.tmp pyproject.toml
    if [ $? -ne 0 ]; then
        echo "Error: Failed to update version in pyproject.toml." >&2
        # Attempt to restore if tmp file exists
        if [ -f "pyproject.toml.tmp" ]; then
            rm pyproject.toml.tmp
        fi
        return 1
    fi
    echo "Successfully updated version in pyproject.toml to ${new_version}"
    return 0
}

# Function to check if Git is installed
check_git_installation() {
    if ! command -v git &> /dev/null; then
        echo "Error: Git is not installed. Please install Git to use this feature." >&2
        return 1
    fi
    return 0
}

# Function to check if the current directory is a Git repository
check_git_repository() {
    if ! git rev-parse --is-inside-work-tree &> /dev/null; then
        echo "Error: This is not a Git repository. Please run this script from the root of a Git repository." >&2
        return 1
    fi
    return 0
}

# Function to check if the Git working tree is clean
check_git_clean_status() {
    if ! git diff --quiet --exit-code; then
        echo "Error: Your Git working tree has uncommitted changes." >&2
        echo "Please commit or stash your changes before proceeding." >&2
        return 1
    fi
    if ! git diff --cached --quiet --exit-code; then
        echo "Error: Your Git index has uncommitted changes (changes staged for commit)." >&2
        echo "Please commit or unstage your changes before proceeding." >&2
        return 1
    fi
    return 0
}

# Function to get the current Git branch name
get_current_git_branch() {
    local branch_name
    branch_name=$(git symbolic-ref --short HEAD 2>/dev/null || git rev-parse --short HEAD 2>/dev/null)
    if [ -z "$branch_name" ]; then
        echo "Error: Could not determine current Git branch." >&2
        return 1
    fi
    echo "$branch_name"
    return 0
}

# Clean up existing dist directory if it exists
if [ -d "dist" ]; then
    echo "Cleaning up existing dist directory..."
    rm -rf dist
fi

# Clean up any previous build artifacts
echo "Cleaning up build artifacts..."
rm -rf build *.egg-info

# Install uv if not already installed
if ! command -v uv &> /dev/null; then
    echo "uv not found. Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
fi

# Create and sync environment using uv
echo "Setting up uv environment..."

# We specifically want to use Python 3.9
uv python pin 3.9

if [ "$DEV_MODE" = true ]; then
    # Development mode installation
    echo "Installing Pycognaize package in development mode..."
    uv sync --all-extras
else
    # Production mode - build and install
    echo "Building distribution package..."
    uv build

    echo "Installing Pycognaize package..."
    uv sync
fi

echo "-----------------------------------------------"
echo "Pycognaize package installed successfully!"
if [ "$DEV_MODE" = true ]; then
    echo "Package installed in development mode."
    echo "You can now import it from other local projects."
    echo ""
    echo "Usage from other projects:"
    echo "1. Add this project as a dependency in your pyproject.toml:"
    echo "   pycognaize = {path = \"/path/to/this/pycognaize/directory\", develop = true}"
    echo ""
    echo "2. Or, install directly in other project:"
    echo "   uv add --path ../path/to/this/pycognaize/directory"
else
    echo "Package installed in production mode."
fi

# Upload package if requested
if [ "$UPLOAD_PACKAGE" = true ]; then
    echo "Preparing for package upload..."

    if ! check_git_installation; then exit 1; fi
    if ! check_git_repository; then exit 1; fi
    if ! check_git_clean_status; then exit 1; fi

    original_branch=$(get_current_git_branch)
    if [ $? -ne 0 ]; then
        echo "Error: Could not determine current Git branch. Aborting upload."
        exit 1
    fi
    echo "Currently on branch: $original_branch"

    new_version_for_tag=""
    version_incremented=false

    if ask_for_version_increment; then
        echo "User chose to increment version."
        current_version_val=$(get_current_version)
        if [ $? -eq 0 ]; then
            echo "Current version: $current_version_val"
            incremented_version=$(increment_patch_version "$current_version_val")
            if [ $? -eq 0 ]; then
                echo "New version will be: $incremented_version"
                # Attempt to unstage pyproject.toml in case it was manually staged before script ran
                git rm --cached pyproject.toml &> /dev/null
                if update_pyproject_version "$incremented_version"; then
                    echo "pyproject.toml updated to version $incremented_version"
                    new_version_for_tag="$incremented_version"
                    version_incremented=true
                else
                    echo "Error updating pyproject.toml. Aborting upload."
                    git checkout -- pyproject.toml &> /dev/null # Attempt to revert
                    exit 1
                fi
            else
                echo "Error incrementing version: $incremented_version. Aborting upload."
                exit 1
            fi
        else
            echo "Error getting current version. Aborting upload."
            exit 1
        fi
    else
        echo "User chose not to increment version."
        current_version_val=$(get_current_version)
        if [ $? -eq 0 ]; then
            new_version_for_tag="$current_version_val"
        else
            echo "Error getting current version even though not incrementing. Aborting."
            exit 1
        fi
    fi

    # Clean up and rebuild
    echo "Cleaning up dist directory for fresh package build..."
    rm -rf dist
    mkdir -p dist

    echo "Building distribution package with version $new_version_for_tag..."
    if ! uv build; then
        echo "Error: uv build failed. Aborting upload."
        # If we changed pyproject.toml, try to revert it
        if [ "$version_incremented" = true ]; then
            git checkout -- pyproject.toml &> /dev/null
        fi
        exit 1
    fi

    # Check for empty dist directory
    if [ ! -d "dist" ] || [ ! "$(ls -A dist)" ]; then
        echo "Error: No distribution files found." ; exit 1 ; fi

    # Install s3pypi if not already installed
    if ! command -v s3pypi &> /dev/null; then
        echo "Installing s3pypi..."
        pip install s3pypi=="2.0.1"
    fi

    # Upload to S3
    echo "Uploading package to S3..."
    if s3pypi upload dist/* --bucket cognaize-pypi --region=eu-central-1; then
        echo "Package uploaded successfully to S3!"

        # Create and push Git tag if version was determined
        if [ -n "$new_version_for_tag" ]; then
            tag_name="v${new_version_for_tag}"
            commit_message="Release version ${new_version_for_tag}"
            if [ "$version_incremented" = true ]; then
                commit_message="Bump version to ${new_version_for_tag}"
            fi

            echo "Committing version change to current branch..."
            if ! git add pyproject.toml; then
                echo "Error: Failed to stage pyproject.toml for commit." >&2
                exit 1
            else
                echo "Committing changes: ${commit_message}"
                if ! git commit -m "${commit_message}"; then
                    echo "Error: Failed to commit version change." >&2
                    if [ "$version_incremented" = true ]; then
                        echo "Reverting pyproject.toml due to commit failure."
                        git checkout -- pyproject.toml &> /dev/null
                    fi
                    exit 1
                else
                    echo "Creating tag: ${tag_name}"
                    if ! git tag -a "${tag_name}" -m "${commit_message}"; then
                        echo "Error: Failed to create tag '${tag_name}'." >&2
                        # Continue anyway since the commit succeeded
                    fi

                    echo "Pushing current branch to origin..."
                    if ! git push origin "$original_branch"; then
                        echo "Error: Failed to push branch ${original_branch}." >&2
                        echo "You may need to push manually with: git push origin ${original_branch}"
                    else
                        echo "Successfully pushed branch ${original_branch}."
                    fi

                    echo "Pushing tag to origin..."
                    if ! git push origin "${tag_name}"; then
                        echo "Error: Failed to push tag '${tag_name}'." >&2
                        echo "You may need to push the tag manually with: git push origin ${tag_name}"
                    else
                        echo "Successfully pushed tag ${tag_name}."
                    fi
                fi
            fi
        fi
    else
        echo "Error: Package upload to S3 failed." >&2
        if [ "$version_incremented" = true ]; then
            echo "Reverting pyproject.toml due to upload failure."
            git checkout -- pyproject.toml &> /dev/null
        fi
        exit 1
    fi
fi

echo "-----------------------------------------------"