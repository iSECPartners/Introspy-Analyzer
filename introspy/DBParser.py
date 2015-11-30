#!/usr/bin/env python
from __future__ import print_function
import sqlite3
import json
import plistlib
import datetime
import six

from .TracedCall import TracedCall
from .IOS_Utils.IOS_ENUM_LIST import IOS_ENUM_LIST
from .IOS_Utils.Signature import Signature
from .IOS_Utils import APIGroups


class DBParser(object):
    """Parses an Introspy DB to extract all function calls stored in it."""

    def __init__(self, dbPath, androidDb):
        """
        Opens the SQLite database at dbPath and extracts all traced calls from it.
        """

        self.dbPath = dbPath
        self.tracedCalls = []
        self.apiGroups = {}
        SqlConn = None
        try:
            rowid = 1
            SqlConn = sqlite3.connect(dbPath).cursor()
            SqlConn.execute("SELECT * FROM tracedCalls")
            for row in SqlConn:

                #TODO: clean this up once android and ios DBs are the same
                if androidDb:
                    callId = row[0]
                    group = six.u(row[1]).encode('ascii','ignore').capitalize()
                    subgroup = six.u(row[2]).encode('ascii','ignore').capitalize()
                    clazz = six.u(row[3])
                    #Hack to display warnings... awful  TODO: remove this
                    method = six.u(row[4])
                    if 'W' in six.u(row[6]):
                        method += ' - [WARNING :' +  six.u(row[7]) + "]"
                    if six.PY2:
                        argsAndReturnValue = self._sanitize_args_dict(plistlib.readPlistFromString(row[5].encode('utf-8')))
                    else:
                        argsAndReturnValue = self._sanitize_args_dict(plistlib.readPlistFromBytes(row[5].encode('utf-8')))

                else:
                    callId = rowid
                    clazz = row[0]
                    method = row[1]
                    subgroup = APIGroups.find_subgroup(clazz, method)
                    group = APIGroups.find_group(subgroup)
                    if six.PY2:
                        argsAndReturnValue = self._sanitize_args_dict(plistlib.readPlistFromString(row[2].encode('utf-8')))
                    else:
                        argsAndReturnValue = self._sanitize_args_dict(plistlib.readPlistFromBytes(row[2].encode('utf-8')))
                    rowid += 1


                self.tracedCalls.append(TracedCall(
                    callId = callId,
                    group = group,
                    subgroup = subgroup,
                    clazz = clazz,
                    method = method,
                    argsAndReturnValue = argsAndReturnValue))

                # Store the api group and subgroup
                if group in self.apiGroups.keys():
                    self.apiGroups[group].append(subgroup)
                else:
                    self.apiGroups[group] = [subgroup]

        except sqlite3.Error as e:
            #print("Fatal error: %s" % e)
            raise

        finally:
            if SqlConn:
                SqlConn.close()

        # Remoe duplicates from subgroups
        for groupName in self.apiGroups.keys():
            self.apiGroups[groupName] = list(set(self.apiGroups[groupName]))


    def get_traced_calls_as_text(self, group=None, subgroup=None):
        """Returns a list of traced calls belonging to the supplied API group and/or subgroup as printable text."""
        for call in self.tracedCalls:
            if group and call.group.lower() != group.lower():
                continue
            if subgroup and call.subgroup.lower() != subgroup.lower():
                continue

            print("  %s" % call)


    def get_traced_calls_as_JSON(self):
        """Returns the list of all traced calls as JSON."""
        tracedCalls_dict = {}
        tracedCalls_dict['calls'] =  self.tracedCalls
        return json.dumps(tracedCalls_dict, default=self._json_serialize)


    def get_API_groups_as_JSON(self):
        """Returns the list of API groups and subgroups as JSON."""
        groupList = []
        for groupName in self.apiGroups.keys():
            subgroupList = []
            for subgroupName in self.apiGroups[groupName]:
                subgroupList.append({'name' : subgroupName})

            groupList.append({'name' : groupName,
                               'subgroups' : subgroupList })

        apigroupsDict = {'groups' : groupList}
        return json.dumps(apigroupsDict, ensure_ascii=True)


    def get_all_URLs(self):
        """Returns the list of all URLs accessed within the traced calls."""
        urlsList = []
        for call in self.tracedCalls:
            if 'request' in call.argsAndReturnValue['arguments']:
                if call.argsAndReturnValue['arguments']['request']['URL']:
                    urlsList.append(call.argsAndReturnValue['arguments']['request']['URL']['absoluteString'])
        # Sort and remove duplicates
        urlsList = list(set(urlsList))
        urlsList.sort()
        return urlsList


    def get_all_files(self):
        """Returns the list of all files accessed within the traced calls."""
        filesList = []
        for call in self.tracedCalls:
            if 'url' in call.argsAndReturnValue['arguments']:
                filesList.append(call.argsAndReturnValue['arguments']['url']['absoluteString'])
            if 'path' in call.argsAndReturnValue['arguments']:
                filesList.append(call.argsAndReturnValue['arguments']['path'])
        # Sort and remove duplicates
        filesList = list(set(filesList))
        filesList.sort()
        return filesList


# TODO: This code crashes with my DB
#    def get_all_keys(self):
#        keysList = []
#        for call in self.traced_calls:
#            if call.method == "SecItemAdd":
#                keysList.append("{0} = {1}".format(call.argsAndReturnValue['arguments']['attributes']['acct'],
#                    call.argsAndReturnValue['arguments']['attributes']['v_Data']))
#            elif call.method == "SecItemUpdate":
#                keysList.append("{0} = {1}".format(call.argsAndReturnValue['arguments']['query']['acct'],
#                    call.argsAndReturnValue['arguments']['attributesToUpdate']['v_Data']))
#        return keysList


    def _sanitize_args_dict(self, argsDict):
        """Goes through a dict of arguments or return values and replaces specific values to make them easier to read."""
        for (arg, value) in argsDict.items():
            if isinstance(value, dict):
                self._sanitize_args_dict(value)
            elif isinstance(value, list):
                sanList = []
                for elem in value:
                    sanList.append(self._sanitize_args_single_value(elem))
                argsDict[arg] = sanList
            else: # Looking at a single value
                argsDict[arg] = self._sanitize_args_single_value(value, arg)

        return argsDict


    @staticmethod
    def _sanitize_args_single_value(value, arg=None):
        """Makes a single value easier to read."""
        if isinstance(value, plistlib.Data):
            try: # Does it seem to be ASCII ?
                return value.data.decode('ascii')
            except UnicodeDecodeError: # No => base64 encode it
                return value.asBase64(maxlinelength=1000000).strip()
        elif isinstance(value, datetime.datetime):
            # Keychain items can contain a date. We just store a string representation of it
            return str(value)
        else:
            # Try to replace this value with a more meaningful string
            if arg in IOS_ENUM_LIST:
                try:
                    if 'mask' in IOS_ENUM_LIST[arg]:
                        has_flag = value & IOS_ENUM_LIST[arg]['mask']
                        if has_flag:
                            return IOS_ENUM_LIST[arg][value]
                    else:
                        return IOS_ENUM_LIST[arg][value]
                except KeyError:
                    return value
            else:
                return value


    @staticmethod
    def _json_serialize(obj):
        """
        Used to specify to json.dumps() how to JSON serialize Signature and TracedCall objects.
        """
        if isinstance(obj, TracedCall) or isinstance(obj, Signature):
            return obj.to_JSON_dict()

