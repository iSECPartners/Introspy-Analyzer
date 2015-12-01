"""
Giant mapping of Classes/Methods and API groups and subgroups.
This affects how we present and group the traced calls for
example when generating an HTML report.
"""
import json, os

API_GROUPS_LIST = []
API_SUBGROUPS_LIST = []

# Data Storage
DATASTORAGE_GROUP = 'DataStorage'
FILESYSTEM_SUBGROUP = 'Filesystem'
USRPREFERENCES_SUBGROUP = 'UserPreferences'
KEYCHAIN_SUBGROUP = 'Keychain'
API_GROUPS_LIST.append(DATASTORAGE_GROUP)
API_SUBGROUPS_LIST.extend([FILESYSTEM_SUBGROUP, USRPREFERENCES_SUBGROUP, KEYCHAIN_SUBGROUP])

# Crypto
CRYPTO_GROUP = 'Crypto'
COMMONCRYPTO_SUBGROUP = 'CommonCrypto'
SECURITY_SUBGROUP = 'SecurityFramework'
API_GROUPS_LIST.append(CRYPTO_GROUP)
API_SUBGROUPS_LIST.extend([COMMONCRYPTO_SUBGROUP, SECURITY_SUBGROUP])

# Network
NETWORK_GROUP = 'Network'
HTTP_SUBGROUP = 'HTTP'
API_GROUPS_LIST.append(NETWORK_GROUP)
API_SUBGROUPS_LIST.extend([HTTP_SUBGROUP])

# IPC
IPC_GROUP = 'IPC'
PASTEBOARD_SUBGROUP = 'Pasteboard'
URISCHEME_SUBGROUP = 'Schemes'
API_GROUPS_LIST.append(IPC_GROUP)
API_SUBGROUPS_LIST.extend([PASTEBOARD_SUBGROUP, URISCHEME_SUBGROUP])

# Misc
MISC_GROUP = 'Misc'
XML_SUBGROUP = 'XML'
API_GROUPS_LIST.append(MISC_GROUP)
API_SUBGROUPS_LIST.extend([XML_SUBGROUP])

API_GROUPS_MAP = {
    FILESYSTEM_SUBGROUP : DATASTORAGE_GROUP,
    USRPREFERENCES_SUBGROUP : DATASTORAGE_GROUP,
    KEYCHAIN_SUBGROUP : DATASTORAGE_GROUP,
    COMMONCRYPTO_SUBGROUP : CRYPTO_GROUP,
    SECURITY_SUBGROUP : CRYPTO_GROUP,
    HTTP_SUBGROUP : NETWORK_GROUP,
    PASTEBOARD_SUBGROUP : IPC_GROUP,
    URISCHEME_SUBGROUP : IPC_GROUP,
    XML_SUBGROUP : MISC_GROUP,
    }


API_SUBGROUPS_MAP = {
    # Filesystem
    'NSData' : FILESYSTEM_SUBGROUP,
    'NSFileHandle' : FILESYSTEM_SUBGROUP,
    'NSFileManager' : FILESYSTEM_SUBGROUP,
    'NSInputStream' : FILESYSTEM_SUBGROUP,
    'NSOutputStream' : FILESYSTEM_SUBGROUP,
    # User Preferences
    'NSUserDefaults' : USRPREFERENCES_SUBGROUP,
    # Keychain
    'SecItemAdd' : KEYCHAIN_SUBGROUP,
    'SecItemCopyMatching' : KEYCHAIN_SUBGROUP,
    'SecItemDelete' : KEYCHAIN_SUBGROUP,
    'SecItemUpdate' : KEYCHAIN_SUBGROUP,
    # Common Crypto
    'CCCryptorCreate' : COMMONCRYPTO_SUBGROUP,
    'CCCryptorCreateFromData' : COMMONCRYPTO_SUBGROUP,
    'CCCryptorUpdate' : COMMONCRYPTO_SUBGROUP,
    'CCCryptorFinal' : COMMONCRYPTO_SUBGROUP,
    'CCCrypt' : COMMONCRYPTO_SUBGROUP,
    'CCHmacInit' : COMMONCRYPTO_SUBGROUP,
    'CCHmacUpdate' : COMMONCRYPTO_SUBGROUP,
    'CCHmacFinal' : COMMONCRYPTO_SUBGROUP,
    'CCHmac' : COMMONCRYPTO_SUBGROUP,
    'CCKeyDerivationPBKDF' : COMMONCRYPTO_SUBGROUP,
    'CC_MD2' : COMMONCRYPTO_SUBGROUP,
    'CC_MD2_Update' : COMMONCRYPTO_SUBGROUP,
    'CC_MD2_Final' : COMMONCRYPTO_SUBGROUP,
    'CC_MD4' : COMMONCRYPTO_SUBGROUP,
    'CC_MD4_Update' : COMMONCRYPTO_SUBGROUP,
    'CC_MD4_Final' : COMMONCRYPTO_SUBGROUP,
    'CC_MD5' : COMMONCRYPTO_SUBGROUP,
    'CC_MD5_Update' : COMMONCRYPTO_SUBGROUP,
    'CC_MD5_Final' : COMMONCRYPTO_SUBGROUP,
    'CC_SHA1' : COMMONCRYPTO_SUBGROUP,
    'CC_SHA1_Update' : COMMONCRYPTO_SUBGROUP,
    'CC_SHA1_Final' : COMMONCRYPTO_SUBGROUP,
    'CC_SHA256' : COMMONCRYPTO_SUBGROUP,
    'CC_SHA256_Update' : COMMONCRYPTO_SUBGROUP,
    'CC_SHA256_Final' : COMMONCRYPTO_SUBGROUP,
    'CC_SHA512' : COMMONCRYPTO_SUBGROUP,
    'CC_SHA512_Update' : COMMONCRYPTO_SUBGROUP,
    'CC_SHA512_Final' : COMMONCRYPTO_SUBGROUP,
    'rand' : COMMONCRYPTO_SUBGROUP,
    'random' : COMMONCRYPTO_SUBGROUP,
    # Security Framework
    'SecPKCS12Import' : SECURITY_SUBGROUP,
    # HTTP
    'NSURLConnection' : HTTP_SUBGROUP,
    'NSURLConnectionDelegate' : HTTP_SUBGROUP,
    'NSURLCredential' : HTTP_SUBGROUP,
    'NSHTTPCookie' : HTTP_SUBGROUP,
    # Pasteboard
    'UIPasteboard' : PASTEBOARD_SUBGROUP,
    # URI Schemes
    'CFBundleURLTypes' : URISCHEME_SUBGROUP,
    'UIApplicationDelegate' : URISCHEME_SUBGROUP,
    'UIApplication' : URISCHEME_SUBGROUP,
    # XML
    'NSXMLParser' : XML_SUBGROUP
}


def find_subgroup(clazz, method):
    """Returns the API subgroup a given class and method belong to."""
    subgroup = None
    try: # Try using the class name
        subgroup = API_SUBGROUPS_MAP[clazz]
    except KeyError:
        # Fall back to using the method name and crash if we can't find it
        subgroup = API_SUBGROUPS_MAP[method]
    return subgroup


def find_subgroup_from_filter(filter):
    # Assuming all filters have one class and one mathod to match at least
    clazz = filter.classes_to_match[0]
    method = filter.methods_to_match[0]
    return find_subgroup(clazz, method)


def find_group(subgroup):
    group = API_GROUPS_MAP[subgroup]
    return group


def get_groups_as_JSON():
    """Converts the list of API groups and subgroups to a JS var declaration."""
    group_list = []
    for group_name in API_GROUPS_LIST:
        subgroup_list = []

        for subgroup_name, group_name2 in API_GROUPS_MAP.items():
            if group_name == group_name2:
                subgroup_list.append({'name' : subgroup_name})

        group_list.append({'name' : group_name,
                           'subgroups' : subgroup_list })

    apigroups_dict = {'groups' : group_list}
    return json.dumps(apigroups_dict)

