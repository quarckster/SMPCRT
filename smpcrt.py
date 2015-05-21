#!/usr/bin/env python
import csv
import sys
import argparse
from piplapis.search import SearchAPIRequest, SearchAPIError


def parseArgs():
    """Parse script parameters and return its values."""
    parser = argparse.ArgumentParser(
        description="Social Media Profile Cross Reference Tool.")
    parser.add_argument("-i",
                        help="input csv file with emails",
                        required=True)
    parser.add_argument("-o",
                        help="output csv file with social profiles",
                        required=True)
    parser.add_argument("-k",
                        help="api key",
                        default="sample_key")
    args = parser.parse_args()
    return args.i, args.o, args.k


def getEmailsFromCsv(inputFile):
    with open(inputFile) as input_csv:
        reader = csv.reader(input_csv, delimiter=';')
        emails = [row[0] for row in reader]
    print "There are %s emails in input file." % len(emails)
    return emails


def getPiplObjects(emails, api_key):
    requests = [SearchAPIRequest(
        email=email, api_key=api_key) for email in emails]
    responses = []
    total = len(requests)
    for i, request in enumerate(requests, 1):
        try:
            print("%s of %s. Getting data for %s." %
                  (i, total, request.person.to_dict()['emails'][0]['display']))
            responses.append(request.send())
        except SearchAPIError as e:
            if e.http_status_code == 500:
                print("Http status code is %s. %s. Going on." %
                      (e.http_status_code, e))
                responses.append("NA")
            elif e.http_status_code == 403:
                print "Http status code is %s. %s" % (e.http_status_code, e)
                break
    return responses


def getProfilesFromResponse(emails, responses):
    data = []
    for response, email in zip(responses, emails):
        profile = {"first name": "NA",
                   "last name": "NA",
                   "email": email,
                   "twitter": "NA",
                   "googleplus": "NA",
                   "linkedin": "NA",
                   "facebook": "NA",
                   "instagram": "NA"}
        try:
            profile["first name"] = response.name.first
        except AttributeError:
            pass
        try:
            profile["last name"] = response.name.last
        except AttributeError:
            pass
        try:
            for url in response.person.urls:
                if url.name == "Facebook" and profile["facebook"] == "NA":
                    profile["facebook"] = url.url
                elif (url.name in ["Google+", "Google Profiles"]
                      and profile["googleplus"] == "NA"):
                    profile["googleplus"] = url.url
                elif url.name == "LinkedIn" and profile["linkedin"] == "NA":
                    profile["linkedin"] = url.url
                elif url.name == "Twitter" and profile["twitter"] == "NA":
                    profile["twitter"] = url.url
                elif url.name == "Instagram" and profile["instagram"] == "NA":
                    profile["instagram"] = url.url
        except AttributeError:
            pass
        data.append(profile)
    return data


def writeOutputToCsv(profiles, outputFile):
    print "Writing data to CSV file."
    with open(outputFile, 'w') as csvfile:
        csvwriter = csv.writer(csvfile,
                               delimiter=';',
                               quotechar='|',
                               quoting=csv.QUOTE_MINIMAL)
        csvwriter.writerow(['first name',
                            'last name',
                            'queried email address',
                            'twitter',
                            'googleplus',
                            'linkedin',
                            'facebook',
                            'instagram'])
        for profile in profiles:
            csvwriter.writerow([profile["first name"],
                                profile["last name"],
                                profile['email'],
                                profile["twitter"],
                                profile["googleplus"],
                                profile["linkedin"],
                                profile["facebook"],
                                profile["instagram"]])
    print "Done."

if __name__ == '__main__':
    emails = getEmailsFromCsv(parseArgs()[0])
    responses = getPiplObjects(emails, parseArgs()[2])
    profiles = getProfilesFromResponse(emails, responses)
    writeOutputToCsv(profiles, parseArgs()[1])
