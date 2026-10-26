# Summary
This Python3 script will connect to the Symphony Google Artifact Repositry *_sym-onprem-gar_* in *_us-east4_* region. It will list all available repositories and allow you to download any available packages.

# Version
2.0.1

# Pre-Requisites
 * You should have access to the *_sym-onprem-gar_* project
   * Follow Symphony on-prem download guide for access and to authenticate the Google Cloud CLI local setup (see details below)
     * https://docs.symphony.com/on-premises-components-documentation/on-premises-components-download-guide
 * Google Cloud CLI should be setup already in your local Linux environment
   * Follow setup guide
     * https://docs.cloud.google.com/sdk/docs/install-sdk
 * Python v3 is required
 * Linux (not tested on Windows)
   * Likely would work on Windows with minor changes

# Usage
 * python3 downloadGARFile.py


# Release Notes
## 2.0.1
 * Added some more comments to the functions

## 2.0.0
 * Restructured to not exit upon download and instead loops through options until user quits
   * Maintains current location in workflow. Example:
     1. Lists repos
	 2. Select repo A
	 3. Lists packages (files) in repo A
	 4. Select package #3
	 5. Download package #3
	 6. Lists packages in repo A
   * Allows backward navigation
   * Allows quitting program
 * Download packages (files) locally in "pretty" format ([filename])
   * Note, the package names in the repos are [pkg-type]:[version]:[filename]
 * Increased error checking
 * Increased coloring
 * Improved list formatting
   * Header row
   * Separator row

## 1.0.0
 * First release
 * List available repositories in project
 * List files in selected repo
 * Download selected file
   * Program exits upon download
 * Basic error checking
 * Basic color coding