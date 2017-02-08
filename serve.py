
import os
import json
from uuid import uuid4
import bottle
import threading
import time
from build.Release.impalapy import ImpalaModule

WORKSPACE = os.path.join(os.getcwd(), 'jobs')
DEFAULT_PORT = 8020

app = bottle.Bottle()

class JobThread(threading.Thread):
	def __init__(self, status_file, basename, files):
		super().__init__()
		self.status_file = status_file
		self.results = {}
		self.basename = basename
		self.files = files

	def run(self):
		print('start job work')
		print(self.basename)
		# print(self.data['files'])
		# do the main work here
		# time.sleep(12000)
		module = ImpalaModule(self.basename)
		for filename, content in self.files.items():
			module.parseFile(filename, content)
		module.generate()
		module.emit_llvm()

		self.status('success')
		print('finish job work')

	def status(self, code):
		print('set status to', code)
		with open(self.status_file, 'w') as file:
			json.dump({'results': self.results, 'status': code}, file)



def workspace(job, *args):
	return os.path.join(WORKSPACE, job, *args)

@app.put('/job')
def create_job():
	job = str(uuid4())
	while os.path.isdir(workspace(job)):
		job = str(uuid4())
	print("job:", job)
	os.makedirs(workspace(job))
	status_file = workspace(job, '.status')
	print(status_file)
	with open(status_file, 'w') as file:
		json.dump({"status":"pending"}, file)
	data = bottle.request.json
	basename = workspace(job, data['module_name'])
	t = JobThread(status_file, basename, data['files'])
	try:
		t.start()
		return bottle.redirect("/job/" + job, 202)
	except RuntimeError as e:
		print(e)
	return bottle.abort(500, 'unable to spawn job')

@app.get('/job/<job>')
def job_status(job):
	status_file = workspace(job, '.status')
	print(status_file)
	if os.path.isfile(status_file):
		with open(status_file, 'r') as file:
			return json.load(file)
	return bottle.abort(404, "job does not exist")

@app.get('/job/<job>/results/<filename>')
def get_result(job, filename):
	return None

if __name__ == '__main__':
	port = int(os.environ.get('PORT', DEFAULT_PORT))
	bottle.run(app, host='0.0.0.0', port=port, debug=True)
