
class Clip:
    ClipName = ''
    ClipTitle = ''
    ClipId = 0
    ClipIndex = 0
    Subtitle = []

    def __init__(self, id, name, title, index):
        self.ClipId = id
        self.ClipName = name
        self.ClipTitle = title
        self.ClipIndex = index

    def __str__(self):
        return 'ClipName: '+ self.ClipName +', ClipTitle: ' + self.ClipTitle \
               +', ClipId: ' +str(self.ClipId)


class Course:
    CourseName = ''
    CourseTitle = ''
    HasTranscript = -1
    Modules = []

    def __init__(self, name, title, has_trans):
        self.CourseName=name
        self.CourseTitle=title
        self.HasTranscript=has_trans

    def __str__(self):
        return 'CourseName: '+ self.CourseName +', CourseTitle: ' + self.CourseTitle \
               +', HasTrans: ' +str(self.HasTranscript)

class Module:
    ModuleName = ''
    ModuleId = 0
    ModuleTitle = ''
    AuthorHandle = ''
    ModuleIndex = 0
    Clips = []

    def __init__(self, id, name, title, authorHandle, moduleIndex):
        self.ModuleId = id
        self.ModuleName = name
        self.ModuleTitle= title
        self.AuthorHandle= authorHandle
        self.ModuleIndex= moduleIndex

    def __str__(self):
        return 'ModuleName: '+ self.ModuleName +', ModuleTitle: ' + self.ModuleTitle \
               +', AuthorHandle: ' +str(self.AuthorHandle)

class ClipTranscript:
    StartTime = 0
    EndTime = -1
    Text = ''

    def __init__(self, startTime, endTime, text):
        self.StartTime = startTime
        self.EndTime = endTime
        self.Text = text

class VirtualFileCache:
    encryptedVideoFile = None
    ReadingTask = None

    def __init__(self, encryptedVideoFilePath):
        self.encryptedVideoFile = encryptedVideoFilePath

    def get_path(self):
        return self.encryptedVideoFile

class VirtualFileStream:

    _Lock = None
    position = 0
    _Cache = None

    def __init__(self, encryptedVideoFilePath):
        self._Cache = VirtualFileCache(encryptedVideoFilePath)

    def clone(self):
        return VirtualFileCache(self._Cache)