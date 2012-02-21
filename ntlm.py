# Author: Michael Franklin, Date: 2/19/12
# This is a simple python module to break ntlm-hashes. It can be run in 
# either brute-force mode or dictionary-mode. This is set by the first 
# argument after the hash to break, as either --brute or --dict. Without
# any options given, it will default to bruteforce mode.
# In brute-force mode, the possible options are:
# --maxlength=[NUM] (tries all passwords up to length NUM
#                    without this option, it defaults to 7)
# --charset=[lower|upper|digits|printable]
#                   (this option can be included multiple times,
#                    each time adding the give charset. printable
#                    is as defined by Python. Default is all lowercase)
# 
# In dictionary mode, the possible options are:
# --dictfile=[FILENAME]
#                   (uses FILENAME as the dictionary. this argument is required)
# --trybrute=[TRUE|FALSE]
#                   (whether or not to try brute force. Default is FALSE. If
#                    true, any number of brute-force options become valid)

import hashlib,binascii
import sys
import string

def gethash(s):
    hash = hashlib.new('md4', s.encode('utf-16le')).digest()
    return binascii.hexlify(hash)

def dict_crack(dictionary_file, hash_to_crack):
    f = open(dictionary_file, 'r')
    passhash = hash_to_crack.lower()
    s = f.read()
    lines = s.split('\n')
    found = False
    hash = ''
    for line in lines:
        line = line.strip()
        hash = gethash(line)
        if hash == passhash:
            return (True, line)
    return (False, '')

def enum_strings(i, char_set, s):
    temp = list()
    if i <= 0:
        return temp
    for c in char_set:
        temp.append(s + c)
    if i <= 1:
        return temp
    to_return = list()
    for current in temp:
        to_append = (enum_strings(i-1, char_set, current))
        for current2 in to_append:
            to_return.append(current2)
    return to_return

class PassEnum:
    
    def __init__(self, numdigits, charsetArg):
        self.digits = list()
        self.charset = charsetArg
        for i in range(numdigits):
            self.digits.append(0)
        self.mod = len(self.charset)
        
    def increment(self):
        for i in range(len(self.digits)):
            self.digits[i] = (self.digits[i] + 1)%self.mod
            if self.digits[i] != 0:
                break
    
    def get_string(self):
        s = ''
        for digit in self.digits:
            s += self.charset[digit]
        return s
        
def brute_crack(hash_to_crack, char_set, max_length):
    passhash = hash_to_crack.lower()
    print char_set
    for i in range(1, max_length):
        print 'Trying passwords of length ' + str(i)
        enumerator = PassEnum(i, char_set)
        max = len(char_set)**i
        print max
        sys.stdout.flush()
        j = 0
        k = 0
        while j < max:
            j += 1
            string_j = enumerator.get_string()
            enumerator.increment()
            thishash = gethash(string_j)
            if passhash == thishash:
                return (True, string_j)
    return (False, '')

def try_brute(sysargv):
    maxlength = 7
    charsets = set()
    charsets.add(string.ascii_lowercase)
    for i in range(3, len(sysargv)):
        if len(sysargv[i].split('=')) == 2:
            option = sysargv[i].split('=')[0]
            value = sysargv[i].split('=')[1]
            if option == '--maxlength':
                maxlength = int(value)
            if option == '--charset':
                if value == 'upper':
                    charsets.add(string.ascii_uppercase)
                if value == 'digits':
                    charsets.add(string.digits)
                if value == 'printable':
                    charsets.add(string.ascii_uppercase)
                    charsets.add(string.digits)
                    charsets.add(string.punctuation)
                    charsets.add(string.whitespace)
                if value == 'nolower':
                    charsets.remove(string.ascii_lowercase)
    charset = ''
    for s in charsets:
        charset += s
    result = brute_crack(sysargv[1], charset, maxlength)
    if result[0]:
        print 'Password is:\t' + result[1]
    else:
        print 'Password is not contained in brute-force search space'

def try_dict(sysargv):
    dictfile = ''
    trybrute = False
    for i in range(3, len(sysargv)):
        if len(sysargv[i].split('=')) == 2:
            option = sysargv[i].split('=')[0]
            value = sysargv[i].split('=')[1]
            if option == '--dictfile':
                dictfile = value
            if option == '--trybrute':
                if value == 'True':
                    trybrute = True
    result = dict_crack(dictfile, sysargv[1])
    if result[0]:
        print 'Password is:\t' + result[1]
    else:
        print 'Password is not in dictionary'
    if trybrute:
        print 'Trying brute-force'

def main(sysargv):
    if len(sysargv) < 2:
        print 'USAGE: python ntlm.py PASSWORD_HASH [options - see top of file]*'
    elif len(sysargv) == 2:
        result = brute_crack(sysargv[1], string.ascii_lowercase, 7)
    else:
        if sysargv[2] == '--brute':
            try_brute(sysargv)
        elif sysargv[2] == '--dict':
            try_dict(sysargv)
                        
                    

if __name__ == '__main__':
    main(sys.argv)
   
