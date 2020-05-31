import json
import os
import pprint
from airtable import Airtable
from feedgen.feed import FeedGenerator
from google.cloud import secretmanager
from google.cloud import storage


at_base_key = "appy55UGrNHNY93mU"
airtable_api_key = ""

if "GCP_PROJECT" in os.environ:
    sclient = secretmanager.SecretManagerServiceClient()
    pname = os.environ["GCP_PROJECT"]
    sname = f"projects/{pname}/secrets/airtable-api-key/versions/latest"
    airtable_api_key = sclient.access_secret_version(sname).payload.data.decode('UTF-8')
else:
    airtable_api_key = os.environ["AIRTABLE_API_KEY"]


def prune_field(fields, to_remove):
    if to_remove in fields:
        del fields[to_remove]
    return fields


def lower_keys(x):
    if isinstance(x, list):
        return [lower_keys(v) for v in x]
    elif isinstance(x, dict):
        return dict((k.lower(), lower_keys(v)) for k, v in x.items())
    else:
        return x


def generate_json_and_rss(event):
    bsnh = Airtable(at_base_key, "Brazilian shirtname holders", api_key=airtable_api_key).get_all(max_records=1000)
    simple_bsnh = {b['id']: b['fields'] for b in bsnh}

    episodes = Airtable(at_base_key, "Episodes", api_key=airtable_api_key).get_all(max_records=1000)
    simple_episodes = {e['id']: e['fields'] for e in episodes}

    experts = Airtable(at_base_key, "Experts", api_key=airtable_api_key).get_all()
    simple_experts = {e['id']: prune_field(e['fields'], "Episodes") for e in experts}

    presenters = Airtable(at_base_key, "Presenters", api_key=airtable_api_key).get_all()
    simple_presenters = {p['id']: prune_field(p['fields'], "Episodes") for p in presenters}

    full_data = lower_keys({
        'bsnh': simple_bsnh,
        'episodes': simple_episodes,
        'experts': simple_experts,
        'presenters': simple_presenters
    })

    # # Generate the RSS feed
    fg = FeedGenerator()
    fg.load_extension('podcast')
    fg.title('World Football Phone In Podcast Archive')
    fg.link(href='http://worldfootballphonein.com', rel='alternate')
    fg.logo('http://worldfootballphonein.com/img/profile.jpg')
    fg.subtitle('Unofficial, fan-curated archive of World Football Phone In show.')
    fg.link(href='http://worldfootballphonein.com/podcasts/rss.xml', rel='self')
    fg.language('en')

    for e in simple_episodes.values():
        if 'Podcast in archive' not in e:
            continue

        e_url = f"https: // worldfootballphonein.com/podcasts/{e['Date'].replace('-', '')}.mp3"
        fe = fg.add_entry()
        fe.id(e_url)
        fe.title('WFPI episode for ' + e['Date'])
        fe.description('Footy talk.')
        fe.enclosure(e_url, 0, 'audio/mpeg')

    db_js = "var wfpiDB=" + json.dumps(full_data, separators=(',', ':')) + ";"

    if "GCP_PROJECT" in os.environ:
        storage_client = storage.Client()
        bucket = storage_client.bucket("wfpi-podcasts-archive")
        db = bucket.blob("db.js")
        db.upload_from_string(db_js)
        rss = bucket.blob("rss.xml")
        rss.upload_from_string(fg.rss_str())
    else:
        with open('db.js', 'w') as outfile:
            outfile.write(db_js)
        fg.rss_file('rss.xml')

    return "OK"
