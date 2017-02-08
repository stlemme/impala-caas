
import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
import time
import os
import sys

ENDPOINT = 'http://localhost:8020/job'

def fetch_request(req):
	try:
		return urlopen(req)
	except HTTPError as e:
		print(e.code, e.reason)
		# print(e.read())  
	except URLError as e:
		print('We failed to reach a server.')
		print('Reason: ', e.reason)
	return None
	
def fetch_json(url):
	req = Request(url)
	response = fetch_request(req)
	data = response.read()
	encoding = response.info().get_content_charset('utf-8')
	content = data.decode(encoding)
	return json.loads(content)


if __name__ == '__main__':
	import argparse

	parser = argparse.ArgumentParser()
	parser.add_argument('-o', '--outfile', required=True)
	parser.add_argument('infiles', nargs='+', type=argparse.FileType('r'))

	args = parser.parse_args()

	# TODO: use list comprehension
	files = dict()
	for file in args.infiles:
		files[file.name] = file.read()

	outfile = os.path.abspath(args.outfile)
	outdir, basename = os.path.split(outfile)

	data = json.dumps({
		"module_name": basename,
		"flags": [],
		"files": files
	}, indent=4).encode('utf8')

	submission = Request(ENDPOINT, data, headers = { 'Content-Type': 'application/json' }, method='PUT')
	response = fetch_request(submission)
	
	if not response or response.status != 202:
		sys.exit(-1)
	
	status_url = response.headers['Location']
	print(status_url, '...', end='', flush=True)

	polling = True
	while polling:
		time.sleep(1)
		data = fetch_json(status_url)
		print('.', end='', flush=True)
		polling = data['status'] == 'pending'

	data = fetch_json(status_url)
	status = data['status']
	
	print('.', status, flush=True)
	if status != 'success':
		sys.exit(-1)

	for outname, url in data['results']:
		print('Fetching', outname, '...', end=' ')
		req = Request(url)
		response = fetch_request(req)
		if response.status != 200:
			print('failed!')
			print('URL:', url)
			sys.exit(-2)
		filename = os.path.join(outdir, outname)
		with open(filename, 'w') as file:
			file.write(response.read())
		print('done.')

