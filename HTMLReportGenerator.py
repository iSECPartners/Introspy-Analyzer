import shutil
import os


class HTMLReportGenerator:
    """
    Generates an HTML report given an analyzed Introspy DB.
    """

    TRACED_CALLS_FILE_NAME =  'tracedCalls.js'
    FINDINGS_FILE_NAME =      'findings.js'
    API_GROUPS_FILE_NAME =    'apiGroups.js'

    # TODO: merge the two templates
    IOS_TEMPLATE_FOLDER = './html-ios'
    ANDROID_TEMPLATE_FOLDER = './html-android'


    def __init__(self, analyzedDB, androidDb):
        self.analyzedDB = analyzedDB
        self.androidDb = androidDb


    def write_report_to_directory(self, outDir):
        # Copy the template
        if self.androidDb:
            shutil.copytree(self.ANDROID_TEMPLATE_FOLDER, outDir)
        else:
            shutil.copytree(self.IOS_TEMPLATE_FOLDER, outDir)

        # Copy the DB file
        shutil.copy(self.analyzedDB.dbPath, outDir)

        # Dump the traced calls
        with open(os.path.join(outDir, self.TRACED_CALLS_FILE_NAME), 'w') as jsFile:
            jsFile.write('var tracedCalls = ' + self.analyzedDB.get_traced_calls_as_JSON() + ';')

        # Dump the findings
        with open(os.path.join(outDir, self.FINDINGS_FILE_NAME), 'w') as jsFile:
            jsFile.write( 'var findings = ' + self.analyzedDB.get_findings_as_JSON() + ';')

        # Dump the API groups
        with open(os.path.join(outDir, self.API_GROUPS_FILE_NAME), 'w') as jsFile:
            jsFile.write('var apiGroups = ' + self.analyzedDB.get_API_groups_as_JSON() + ';')

