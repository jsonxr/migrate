import os
import pickle
import hashlib


class _PickledFile(object):
    def __init__(self):
        self.filehash = None
        self.obj = None


def _githash(data):
    s = hashlib.sha1()
    s.update("blob %u\0" % len(data))
    s.update(data)
    return s.hexdigest()


def load(root, filename, create):
    pickle_root = root + "/.cache"
    pickle_file = pickle_root + filename
    if not os.path.exists(os.path.dirname(pickle_file)):
        os.makedirs(os.path.dirname(pickle_file))
    actual_file = root + filename
    # Get the file contents
    with file(actual_file, 'r') as stream:
        string = stream.read()
    filehash = _githash(string)
    # Get the pickled cache file if the hash is the same
    if os.path.exists(pickle_file):
        with open(pickle_file, 'r') as stream:
            pickledFile = pickle.load(stream)
            if pickledFile.filehash == filehash:
                return pickledFile.obj
    # Save the object in the cache
    obj = create()
    obj.load_from_str(string)
    with open(pickle_file, 'w') as stream:
        pickledFile = _PickledFile()
        pickledFile.filehash = filehash
        pickledFile.obj = obj
        pickle.dump(obj, stream, pickle.HIGHEST_PROTOCOL)
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
