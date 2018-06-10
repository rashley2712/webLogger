#!/usr/bin/env python3
import argparse
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Produces fake ParameterNoticeBoard output.')
    parser.add_argument('-i', type=str, help='parameter to report' )
    arg = parser.parse_args()

    fakeFile = open('fakeParameters.txt', 'rt')

    parameters = []
    for line in fakeFile:
        goodLine = line.strip()
        parameters.append(goodLine)
    fakeFile.close()

    if arg.i is None:
        for p in parameters:
            print(p)
    else:
        for p in parameters:
            params = p.split()
            keyword = params[0].split('-')[0]
            if keyword == arg.i:
                print(params[-1])