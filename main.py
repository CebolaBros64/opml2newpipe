import argparse, json, re
import xml.etree.ElementTree as ET

from pprint import pprint

progName = 'opml2newpipe'
progDesc = 'Converts a OPML file into a NewPipe-compatible .json file.'


def get_service(_str):
    regex = r"https?://(.+\.)?(?P<service>.+)\.com"  # Regex to get domain name

    table = {'youtube': 0,  # Translation table
             'soundcloud': 1,
             'bandcamp': 4
             }

    url_name = re.search(regex, _str, re.IGNORECASE) \
        .group('service')  # Find domain name in string, and store in var

    for domain_name in list(table.keys()):  # Loop through every item in
        #                                     table
        if domain_name in url_name:  # If a certain domain is found...
            return table[domain_name]  # ...return its equivalent value


def get_name(_str, domain):
    regex = r"Stream (?P<name>.+?)( music)? \| Listen to (.+) for free on SoundCloud"

    if domain == 1:  # Soundcloud
        return re.search(regex, _str).group('name')  # get rid of junk
    else:
        return _str  # Return as is


def sanitize_url(_str, domain):
    """ This func could be better """
    sc_list = (
                "/tracks",
                "/sets"
            )

    bc_list = (
                "music",
                "community"
            )

    if domain == 1:  # Soundcloud
        for sufix in sc_list:
            if _str.endswith(sufix):
                return _str[:-len(sufix)]
    elif domain == 4:  # Bandcamp
        for sufix in bc_list:
            if _str.endswith(sufix):
                return _str[:-len(sufix)]
    return _str


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog=progName, description=progDesc)
    parser.add_argument('i_path',
                        metavar='input',
                        nargs=1,
                        help='Input OPML file')
    parser.add_argument('o_path',
                        metavar='output',
                        nargs=1,
                        help='Output JSON file')
    args = parser.parse_args()

    newpipe_out = {
        # 'app_version": "0.21.13',
        # 'app_version_int': 979,
    }

    tree = ET.parse(args.i_path[0])
    root = tree.getroot()

    fraidycat_follows = []

    for child in root:
        print(child.tag, child.attrib)

    for i in root.iter('outline'):
        url = i.attrib['htmlUrl']

        service = get_service(url)
        name = get_name(i.attrib['text'], service)

        url = sanitize_url(i.attrib['htmlUrl'], service)

        fraidycat_follows.append({
            "service_id": service,  # 0 = Youtube,
            #                         1 = Soundcloud,
            #                         4 = Bandcamp
            "url": url,
            "name": name
        })

    # pprint(subscriptions)
    newpipe_out['subscriptions'] = fraidycat_follows

    pprint(newpipe_out)

    with open(args.o_path[0], 'w') as f:
        f.write(json.dumps(newpipe_out))
