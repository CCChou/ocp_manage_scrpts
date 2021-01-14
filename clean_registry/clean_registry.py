import httplib
import json

def main():
    URL = 'localhost'
    PORT = 5000

    conn = getconnection(URL, PORT) 
    repos = getrepos(conn)
    print('find %s repositories' % len(repos))

    for repo in repos:
        tags = gettags(conn, repo)
        print('find %s in %s repository' % (len(tags), repo))

        for tag in tags:
            digest = getdigest(conn, repo, tag)
            print('deleting image "%s/%s" with manifest "%s"' % (repo, tag, digest))
            msg = deleteimage(conn, repo, digest)
            #print('deletion %s' % msg)

def getconnection(url, port):
    return httplib.HTTPConnection(url, port)

def getrepos(conn):
    conn.request('GET', '/v2/_catalog')
    res = conn.getresponse()
    data = res.read()
    return json.loads(data)['repositories']

def gettags(conn, repo):
    conn.request('GET', '/v2/' + repo + '/tags/list')
    res = conn.getresponse()
    return json.loads(res.read())['tags']

def getdigest(conn, repo, tag):
    headers = {'Accept': 'application/vnd.docker.distribution.manifest.v2+json'}
    url = '/v2/%s/manifests/%s' % (repo, tag)
    conn.request('GET', url, headers=headers)
    res = conn.getresponse()
    res.read()
    return res.getheader('docker-content-digest')

def deleteimage(conn, repo, digest):
    headers = {'Accept': 'application/vnd.docker.distribution.manifest.v2+json'}
    url = '/v2/%s/manifests/%s' % (repo, digest)
    conn.request('DELETE', url, headers=headers)
    res = conn.getresponse()
    #if res.status == 200:
    #    return 'success'
    #else:
    #    return 'fail ' + res.read()


if __name__ == '__main__':
    main()
