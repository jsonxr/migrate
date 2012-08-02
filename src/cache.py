import os
import cPickle
import hashlib

'''
load(root, filename, create)

Object passed in as "create" must implement the
load_from_str(self, content)
method.
'''


class _PickledFile(object):
    def __init__(self):
        self.filehash = None
        self.obj = None


def _githash(data):
    s = hashlib.sha1()
    s.update("blob %u\0" % len(data))
    s.update(data)
    return s.hexdigest()


def load(project_root, filename, create):
    filename = filename.replace(project_root, '')
    pickle_root = project_root + "/.cache"
    pickle_file = pickle_root + filename + ".pickle"
    actual_file = project_root + filename
#    print("cache.load-------------------")
#    print("filename=%s" % filename)
#    print("pickle_root=%s" % pickle_root)
#    print("pickle_file=%s" % pickle_file)
#    print("actual_file=%s" % actual_file)

    if not os.path.exists(os.path.dirname(pickle_file)):
        os.makedirs(os.path.dirname(pickle_file))
    # Get the file contents
    with file(actual_file, 'r') as stream:
        string = stream.read()
    filehash = _githash(string)
    # Get the pickled cache file if the hash is the same
    if os.path.exists(pickle_file):
        with open(pickle_file, 'r') as stream:
            try:
                pickledFile = cPickle.load(stream)
                if pickledFile.filehash == filehash:
                    #print("return from cache")
                    return pickledFile.obj
            except:
                #print("error trying to retrieve pickle")
                # If there are any errors, we will just create normally
                pass
    # Save the object in the cache
    #print("create()")
    obj = create()
    obj.load_from_str(string)
    with open(pickle_file, 'w') as stream:
        pickledFile = _PickledFile()
        pickledFile.filehash = filehash
        pickledFile.obj = obj
        cPickle.dump(pickledFile, stream, cPickle.HIGHEST_PROTOCOL)
    return obj

#
#def githash(data):
#    s = hashlib.sha1()
#    s.update("blob %u\0" % len(data))
#    s.update(data)
#    return s.hexdigest()
#
#
#def load_version_from_pickle(name, filename):
#    pickle_file = filename + ".pickle"
#    print("pickle_file=" + pickle_file)
#    version = None
#
#    if os.path.exists(pickle_file):
#        with open(pickle_file, 'r') as stream:
#            version = pickle.load(stream)
#            thehash = version.filehash
#
#            with file(filename, 'r') as stream:
#                string = stream.read()
#            filehash = githash(string)
#            if (thehash == filehash):
#                return version
#            else:
#                version = None
#                print("cache invalid")
#
#    if not version:
#        version = Version()
#        version.name = name
#        version.filename = filename
#        version.load_from_file()
#        save_version_to_pickle(version, pickle_file)
#        return version
#
#
#def save_version_to_pickle(version, filename):
#    print("save pickle_file=" + filename)
#    with open(filename, 'w') as stream:
#        pickle.dump(version, stream, pickle.HIGHEST_PROTOCOL)
