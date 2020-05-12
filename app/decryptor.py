import colorama # pip install colorama
from colorama import Fore, Style
import sys, getopt
from app.models import Course, Module, Clip, ClipTranscript, VirtualFileStream
from app.sqlite_reader import SqliteReader
from app.utils import *
import os, sys
import base64


class DecryptorOptions:
    UseDatabase = False
    UseOutputFolder = False
    RemoveFolderAfterDecryption = False
    UsageCommand = False
    CreateTranscript = False
    InputPath = ''
    DatabasePath = ''
    OutputPath = ''

    def __init__(self, argv):
        try:
            opts, args = getopt.getopt(argv, 'hf:d:o:', ['help','files_path=', 'db_path=', 'out_path='])
        except getopt.GetoptError:
            Utils.print_help_command()
            sys.exit(2)

        for opt, arg in opts:
            if opts == '-h':
                print('run.py -f [PATH] -d [DB_PATH]')
                sys.exit()
            elif opt in ('-f','--file_path'):
                self.InputPath = arg
            elif opt in('-d', '--db_path'):
                self.DatabasePath = arg
            elif opt in('-o', '--out_path'):
                self.OutputPath = arg
            else:
                Utils.print_help_command()
        #print('Path: ', self.InputPath)
        #print('DB Path: ', self.DatabasePath)
        #print('Output Path: ', self.OutputPath)

class Decryptor:
    InvalidPathCharacters = []
    InvalidFileCharacters = []
    Options = None
    color_default = None
    TaskList = []

    def __init__(self, decryptorOptions):
        self.Options = decryptorOptions
        self.InvalidPathCharacters = [':', '?', '"', '\\', '/']
        self.InvalidFileCharacters = [':', '?', '"', '\\', '/']

    def decryptAllFolders(self, folderPath, outputFolder):

        # Make sure folderPath exists
        if not os.path.exists(folderPath):
            print('Directory does not exists!')
            sys.exit(2)
        # Create outputFolder if it doesn't exist
        if not os.path.exists(outputFolder):
            os.mkdir(outputFolder)

        courses = []
        # Loop through each file recursively
        for root_path, subDirs, files in os.walk(folderPath):
            for file_name in files:
                if file_name.lower().endswith('.psv'):
                    course_path = os.path.join(root_path, file_name)
                    #print( 'Course Path: ', course_path )

                    course = self.getCourseFromDb(root_path)
                    courses.append(course)
                    newCoursePath = os.path.join(outputFolder, self.cleanName(course.CourseTitle))

                    # Create the new directory if doesn't exist
                    if not os.path.exists(newCoursePath):
                        os.mkdir(newCoursePath)

                    # Get list all modules in current course
                    modules = course.Modules
                    if len(modules) > 0:
                        for module in modules:
                            # Generate module hash name
                            moduleHash = self.moduleHash(module.ModuleName, module.AuthorHandle)
                            #print('moduleHash:',moduleHash)
                            # Generate module path
                            course_dir_path = os.path.dirname(root_path)
                            moduleHashPath = os.path.join(course_dir_path, moduleHash)

                            #print('moduleHashPath:',moduleHashPath)
                            # Create new module path with decryption name
                            newModulePath = os.path.join(newCoursePath,
                                                         str(module.ModuleIndex) + ". " + module.ModuleTitle)
                            #print('newModulePath: ',newModulePath)

                            # If length too long, rename it
                            if len(newModulePath) > 240:
                                newModulePath = os.path.join(course_path, str(module.ModuleIndex))

                            #print('looking for path: ', moduleHashPath)
                            if os.path.exists(moduleHashPath):
                                if os.path.exists(newModulePath):
                                    print('Creating: ', newModulePath)
                                    os.mkdir(newModulePath)
                                self.decryptAllVideos(moduleHashPath, module, newModulePath)
                            else:
                                print(Fore.RED + "Folder: ", moduleHash ," cannot be found in the current course path."+ Style.RESET_ALL)
                                #sys.exit(0)
                    else:
                        print(Fore.MAGENTA + "Decryption ", course.CourseTitle, " has been completed!" + Style.RESET_ALL)


    def cleanName(self, path):
        for invalid_char in self.InvalidFileCharacters:
            path = path.replace(invalid_char, '-')
        return path

    # Returns Course object from db info
    def getCourseFromDb(self, folderCoursePath):
        courseName = self.getFolderName(folderCoursePath, True).strip().lower()
        #print('courseName: ', courseName)
        return self.getCourseInfo(courseName)

    def getFolderName(self, folderPath, checkExisted = False): # checkExisted not used here
        return os.path.basename(os.path.dirname(folderPath))

    def getCourseInfo(self, courseName):
        db = SqliteReader(self.Options.DatabasePath)
        row = db.find_one('''SELECT Name, Title, HasTranscript
                                FROM Course
                                WHERE Name = ?''', [courseName])
        course = Course(name=row[0], title=row[1], has_trans=row[2])
        course.Modules = self.getModulesFromDb(db, courseName)
        #print(course.CourseName,': ', course.CourseTitle)
        db.close()
        return course

    def getModulesFromDb(self, db, courseName):
        modules = []
        if db.is_connected():
            rows = db.find_all('''SELECT Id, Name, Title, AuthorHandle, ModuleIndex
                                FROM Module
                                WHERE CourseName = ?''', [courseName])
            for row in rows:
                module = Module(row[0], row[1], row[2], row[3], row[4])
                module.Clips = self.getClipsFromDb(db, row[0])
                #print(module)
                modules.append(module)
        return modules

    def getClipsFromDb(self, db, moduleId):
        clips = []
        if db.is_connected():
            rows = db.find_all('''SELECT Id, Name, Title, ClipIndex
                                FROM Clip
                                WHERE ModuleId = ?''', [moduleId])
            for row in rows:
                clip = Clip(row[0], row[1], row[2], row[3])
                clip.Subtitle = self.getTrasncriptFromDb(db, row[0])
                clips.append(clip)
        return clips

    def getTrasncriptFromDb(self, db, clipId):
        list = []
        if db.is_connected():
            rows = db.find_all('''SELECT StartTime, EndTime, Text
                                FROM ClipTranscript
                                WHERE ClipId = ?
                                ORDER BY Id ASC''', [clipId])
            for row in rows:
                clip_transcript = ClipTranscript(row[0], row[1], row[2])
                list.append(clip_transcript)
        return list


    def decryptAllVideos(self, folderPath, module, outputPath):
        #print('Decrypting: ', folderPath, module, outputPath)
        clips = module.Clips
        for clip in clips:
            # Get current path of the encrypted video
            currPath = os.path.join(folderPath, clip.ClipName + '.psv')
            if os.path.exists(currPath):
                # Create new path with output folder
                newPath = os.path.join(outputPath, str(clip.ClipIndex) + ". " + clip.ClipTitle + ".mp4")
                # If length too long, rename it
                if len(newPath) > 240:
                    newPath = os.path.join(outputPath, str(clip.ClipIndex) + ".mp4")
                #print(newPath)
                playingFileStream = VirtualFileStream(currPath)
                iStream = playingFileStream.clone()
                fileName = os.path.basename(currPath)
                print(Fore.YELLOW + "Start to Decrypt File: "+Style.RESET_ALL, fileName)
                self.decryptVideo(iStream, newPath)
                if self.Options.CreateTranscript:
                    self.writeTranscriptFile(clip, newPath)
            else:
                print('Path not found: ', currPath)


    def moduleHash(self, moduleName, moduleAuthorName):
        #print('moduleName: ', moduleName)
        s = bytes(moduleName + "|" + moduleAuthorName, 'utf-8')
        #return str(base64.b64encode(Utils.md5(str(s.encode())))).replace('/', '_')
        #b64 = base64.urlsafe_b64encode((bytes(md5, 'utf-8')))
        #b64 = base64.standard_b64encode((bytes(md5, 'utf-8')))
        return str( base64.b64encode( Utils.md5(s) ) , 'utf-8').replace('/', '_')
        #using (MD5 md5 = MD5.Create())
        #    return Convert.ToBase64String(md5.ComputeHash(Encoding.UTF8.GetBytes(s))).Replace('/', '_');

    def decryptVideo(self, curStream, newPath):
        print('decrypting from:', curStream.encryptedVideoFile.get_path(), ', to:', newPath)
        if os.path.exists(newPath):
            os.remove(newPath)
        # read data byte by byte
        #with open(newPath, "wb") as f:
        #    for byte in bytearray(open(curStream.get_path(), "rb").read()):
                #f.write(bytes(chr(byte ^ 101), 'iso_8859_1')) # this works for mac version

    # Not yet implemented
    def writeTranscriptFile(self, clip, clipPath):
        clipTranscripts = clip.Subtitle
        if len(clipTranscripts) > 0:
            transcriptPath = os.path.join(os.path.basename(clipPath),
                                          os.path.dirname(clipPath) + ".srt")
            if not os.path.exists(transcriptPath):
                # Write it to file with stream writer
                #StreamWriter writer = new StreamWriter(transcriptPath);
                #int i = 1;
                #foreach (var clipTranscript in clipTranscripts)
                #{
                #    var start = TimeSpan.FromMilliseconds(clipTranscript.StartTime).ToString(@"hh\:mm\:ss\,fff");
                #    var end = TimeSpan.FromMilliseconds(clipTranscript.EndTime).ToString(@"hh\:mm\:ss\,fff");
                #    writer.WriteLine(i++);
                #    writer.WriteLine(start + " --> " + end);
                #    writer.WriteLine(clipTranscript.Text);
                #    writer.WriteLine();
                #}
                #writer.Close();
                #WriteToConsole("Transcript of " + Path.GetFileName(clipPath) + " has been generated scucessfully.",
                #    ConsoleColor.Red);
                pass