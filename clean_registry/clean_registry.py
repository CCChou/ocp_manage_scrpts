import httplib
import json

HOST = 'localhost'
PORT = 5000
conn = None

def main():
    initconnection()
    repos = getrepos()
    if repos is None:
        print('No repositories found')
    else:
        print('Find %s repositories' % len(repos))

    for repo in repos:
        tags = gettags(repo)
        if tags is None:
            continue
        print('Find %s tags in %s repository' % (len(tags), repo))

        for tag in tags:
            digest = getdigest(repo, tag)
            print('Deleting image "%s/%s" with manifest "%s"' % (repo, tag, digest))
            msg = deleteimage(repo, digest)
            print('Deletion %s' % msg)
            
    conn.close() 

def initconnection():
    global conn = httplib.HTTPConnection(HOST, PORT)

def getrepos():
    conn.request('GET', '/v2/_catalog')
    res = conn.getresponse()
    data = res.read()
    return json.loads(data)['repositories']

def gettags(repo):
    conn.request('GET', '/v2/' + repo + '/tags/list')
    res = conn.getresponse()
    return json.loads(res.read())['tags']

def getdigest(repo, tag):
    headers = {'Accept': 'application/vnd.docker.distribution.manifest.v2+json'}
    url = '/v2/%s/manifests/%s' % (repo, tag)
    conn.request('GET', url, headers=headers)
    res = conn.getresponse()
    res.read()
    return res.getheader('docker-content-digest')

def deleteimage(repo, digest):
    headers = {'Accept': 'application/vnd.docker.distribution.manifest.v2+json'}
    url = '/v2/%s/manifests/%s' % (repo, digest)
    conn.request('DELETE', url, headers=headers)
    res = conn.getresponse()
    data = res.read()
    if res.status % 100 == 2:
        return 'success, status: %s' % res.status
    else:
        return 'fail, status: %s, msg: %s' % (res.status, data)


if __name__ == '__main__':
    main()
