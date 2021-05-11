import sys
import argparse
import logging
import json
import datetime
import csv
from urllib import parse

import anticrlf
from veracode_api_py import VeracodeAPI as vapi, Workspaces

log = logging.getLogger(__name__)

def setup_logger():
    handler = logging.FileHandler('vcscalicense.log', encoding='utf8')
    handler.setFormatter(anticrlf.LogFormatter('%(asctime)s - %(levelname)s - %(funcName)s - %(message)s'))
    logger = logging.getLogger(__name__)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

def creds_expire_days_warning():
    creds = vapi().get_creds()
    exp = datetime.datetime.strptime(creds['expiration_ts'], "%Y-%m-%dT%H:%M:%S.%f%z")
    delta = exp - datetime.datetime.now().astimezone() #we get a datetime with timezone...
    if (delta.days < 7):
        print('These API credentials expire ', creds['expiration_ts'])

def get_all_workspaces():
    return Workspaces().get_all()

def get_libraries_for_workspace(guid):
    return Workspaces().get_libraries(workspace_guid=guid, unmatched=False)

def get_licenses_for_libraries(libraries):
    all_licenses = []
    for lib in libraries:
        status = 'Getting license information for library {}'.format(lib['id'])
        print(status)
        log.info(status)
        lib_detail = Workspaces().get_library(lib['id'])
        all_licenses.append(lib_detail)
    return all_licenses

def write_licenses_to_csv(ws_licenses):
    status = 'Writing licenses list to vcscalicense.csv'
    print(status)
    log.info(status)
    fields = [ 'workspace_id','workspace_name','library_id','library_name','version','license_name','license_risk' ]

    with open("vcscalicense.csv", "w", newline='') as f:
        w = csv.DictWriter(f, fields)
        w.writeheader()
        for k in ws_licenses:
            w.writerow({'workspace_id': '','workspace_name': '','library_id': k['id'], 
                        'library_name': k['name'], 'version': k['version'], 
                        'license_name': k['licenses'][0]['name'], 
                        'license_risk': k['licenses'][0]['risk'] })


def prompt_for_workspace(prompt_text):
    guid = ""
    ws_name_search = input(prompt_text)
    ws_candidates = Workspaces().get_by_name(parse.quote(ws_name_search))
    if len(ws_candidates) == 0:
        print("No matches were found!")
    elif len(ws_candidates) > 1:
        print("Please choose a workspace:")
        for idx, wsitem in enumerate(ws_candidates,start=1):
            print("{}) {}".format(idx, wsitem["name"]))
        i = input("Enter number: ")
        try:
            if 0 < int(i) <= len(ws_candidates):
                guid = ws_candidates[int(i)-1].get('id')
        except ValueError:
            guid = ""
    else:
        guid = ws_candidates[0].get('id')

    return guid

def process_workspace(ws_guid):
    status = "Checking workspace {} for a list of licenses".format(ws_guid)
    log.info(status)
    print(status)
    this_library_list = get_libraries_for_workspace(ws_guid)
    if this_library_list is None:
        print('No libraries for workspace {}'.format(ws_guid))
        return
    return this_library_list

def main():
    parser = argparse.ArgumentParser(
        description='This script exports licenses for the libraries in the specified workspace(s).')
    parser.add_argument('-w', '--workspace', required=False, help='Workspace guid to check for library licenses.',default='7ac1fcd4-89c7-4f2e-808c-157a232c58d9')
    parser.add_argument('--all', '-l',action='store_true', help='Set to report for library licenses for all workspaces.',default=False)
    parser.add_argument('--prompt', '-p',action='store_true', help='Prompts for name of the workspace to check for library licenses.')
    args = parser.parse_args()

    ws_guid = args.workspace
    checkall = args.all
    prompt = args.prompt
    setup_logger()

    # CHECK FOR CREDENTIALS EXPIRATION
    creds_expire_days_warning()

    if prompt:
        ws_guid = prompt_for_workspace("Enter the workspace name to check for licenses:")

    wscount=0
    ws_libraries=0
    ws_licenses=0
    all_ws_libraries = []
    all_ws_licenses = []

    if checkall:
        wslist = get_all_workspaces()
        status = "Checking {} workspaces for a list of licenses".format(len(wslist))
        log.info(status)
        print(status)
        for ws in wslist:
            ws_guid = ws.get('id')
            this_library_list = process_workspace(ws_guid)
            if this_library_list is None or len(this_library_list) == 0:
                continue
            ws_library_count = len(this_library_list)
            wscount += 1
            ws_libraries += ws_library_count
            if wscount % 10 == 0:
                print("Checked {} workspaces and counting".format(wscount))
            all_ws_libraries.extend(this_library_list)

    elif ws_guid != None:
        this_library_list = process_workspace(ws_guid)
        if this_library_list is None:
            return

        ws_library_count = len(this_library_list)
        if ws_library_count > 0:
            wscount = 1
            ws_libraries += ws_library_count
        all_ws_libraries.extend(this_library_list)
    else:
        print('You must either provide a workspace slug or check all workspaces.')
        return

    print('Found {} libraries'.format(ws_libraries))

    all_ws_licenses = get_licenses_for_libraries(all_ws_libraries)

    ws_licenses = len(all_ws_licenses)
    
    write_licenses_to_csv(all_ws_licenses)

    print("Found {} workspaces with {} licenses. See vcscalicense.csv for details.".format(wscount,ws_licenses))
    log.info("Found {} workspaces with {} licenses.".format(wscount,ws_licenses))
    
if __name__ == '__main__':
    main()