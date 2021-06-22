# Veracode SCA License Report

Get a CSV report of the licenses for the libraries in your Veracode SCA Agent workspace.

## Setup

NOTE: This script requires Python 3!

Clone this repository:

    git clone https://github.com/tjarrettveracode/veracode-sca-license-report

Install dependencies:

    cd veracode-sca-license-report
    pip install -r requirements.txt

(Optional) Save Veracode API credentials in `~/.veracode/credentials`

    [default]
    veracode_api_key_id = <YOUR_API_KEY_ID>
    veracode_api_key_secret = <YOUR_API_KEY_SECRET>

## Run

If you have saved credentials as above you can run:

    python vcscalicense.py (arguments)

Otherwise you will need to set environment variables:

    export VERACODE_API_KEY_ID=<YOUR_API_KEY_ID>
    export VERACODE_API_KEY_SECRET=<YOUR_API_KEY_SECRET>
    python vcscalicense.py (arguments)

Arguments supported include:

* --workspace, -w  (opt): "slug" of the workspace for which to produce the license report.
* --prompt, -p (opt): If set, prompts for the workspace name for which to run the report.
* --all, -l (opt): If set, checks all workspaces.

## NOTES

1. All values are output to vcscalicense.csv
