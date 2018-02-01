import gitlab
import os
import shutil
import argparse
import subprocess as sp

parser = argparse.ArgumentParser(description='Automatically create a repo and deploy website')
parser.add_argument('--folder', '-d', type=str, required=True, help='directory containing repo content')
parser.add_argument('--name', '-n', type=str, default=None, help='name of the project repo to be created')

args = parser.parse_args()

websiteContentDir = args.folder
studentName = None
if args.name == None:
	studentName = input('Type your name: ')
else:
	studentName = args.name


gl = gitlab.Gitlab.from_config('7mcstudentpub')
groupName = '7mc-students-pub'
#groupId = gl.groups.search(groupName)[0].id
groupId = 2455665



project = gl.projects.create({
	'name': studentName, 
	'namespace_id': groupId,
	'visibility': 'public'
})

upstreamURL = project.ssh_url_to_repo
webURL = project.web_url

print('Project successfully created', webURL)

# Add url to repo at bottom of page
homepage = os.path.join(websiteContentDir, 'index.html')
with open(homepage, 'r+') as f:
	htmlStr = f.read()
	aTag = '<a href={} target="_blank">Find the code for this here</a>'
	aTag = aTag.format(webURL)
	htmlStr = htmlStr.replace('</body>', aTag + '\n</body>')
	f.seek(0)
	f.write(htmlStr)
	f.truncate()

folder = os.path.join('../', studentName + '-website')
shutil.copytree(websiteContentDir, folder)
shutil.copy('.gitlab-ci.yml', folder)

sp.call(['git', 'init'], cwd=folder)
sp.call(['git', 'remote', 'add', 'origin', upstreamURL], cwd=folder)
sp.call(['git', 'add', '-A'], cwd=folder)
sp.call(['git', 'commit', '-m', '"init"'], cwd=folder)
sp.call(['git', 'push', '-u', 'origin', 'master'], cwd=folder)

print('Site should be live at:', 'https://7mc-students-pub.gitlab.io/' + project.name)
