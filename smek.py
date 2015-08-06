import tty,sys
import termios
import string
from soundeffects import SoundEffect

'''
7/18/2015 - Ken Robbins

Utility to read keys from the IPAC-4 that is plugged
in to a USB port and appears like a raw USB keyboard.

Key     Base 10 integer value       SMEK connection     Pin
a-z     97-122      <26 keys>       S1-S26              1COIN-3UP
0-9     48-57       <10 keys>       S27-S36             3LEFT-4SW4

<12 keys>
'-'     45  Minus                   S37                 4SW5
'.'     46  Period                  S38                 4SW6
'
Currently, the IPAC-4 is programmed as follows:
    a-z         S1-S26  [1COIN-3UP]
    0-9         S27-S36 [3LEFT-4SW4]
    minus       S37     [4SW5]
    period      S38     [4SW6]
    See README for intermediate used mappings
    ENTER       S39 (EXECUTE) [2COIN]

The order is clockwise around the board starting with 1COIN where 1COIN is on the upper left looking at the component side of the board.
'''

def mapCharToSwitchNumber(ch):
    ''' Return the switch number (1 based) corresponding to the character. 0 if unmappable. '''
    idx = 0
    if ch.islower():
        idx = ord(ch) - ord('a') + 1    # Map a-z to 1-26
    elif ch.isdigit():
        idx = ord(ch) - ord('0') + 27   # Map 0-9 to 27-36
    elif ch == '-':
        idx = 37                        # Map '-' to 37
    elif ch == '.':
        idx = 38                        # Map '.' to 38

    return idx

class SMEK:
    ''' Read commands from the IPAC-4 encoder of SMEK switch state '''
    def __init__(self, quitChar, keyHandler = None):
        self.clearState()
        self.quitChar = quitChar
        self.EXECUTE_KEY = 13    # ENTER key code in decimal
        self.keyHandler = keyHandler

    def clearState(self):
        '''
        sequence is the string of keys pressed, in order, since the last EXECUTE.
        Since we don't know if a CLEAR was pressed this is an unreliable
        representation of state.
        May include repeats if a CLEAR was pressed in between key entries.
        '''
        self.sequence = ''

        ''' The switch state at the time EXECUTE was pressed '''
        self.command = [False] * 41 # Initialize 41 elements to False (0 element is not used)

    def readChar(self):
        ''' Read a character from stdio in a raw (read immediately without enter key) mode '''
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

    def updateState(self, ch):
        '''
        Map SMEK switches to an array showing the switch state
        Mapping:
            S1-S36 to a-z and 0-9
            S37 to minus '-'
            S38 to dash '.'
            S39 (EXECUTE) to ENTER
            CLEAR is not wired

        command is a list indexed by key SMEK key switch number where an element is
        True if the key was pressed at the time of the EXECUTE command.
        sequence is the list of keypresses detected

        Return False if key cannot be mapped, otherwise return True
        '''

        idx = mapCharToSwitchNumber(ch)
        if idx == 0:
            print 'Unhandled mapping. Ordinal value of key was ' + str(ord(ch))
            return False

        # Update state
        self.sequence += ch
        self.command[idx] = True

        if self.keyHandler:
            self.keyHandler(ch)

        return True

    def getState(self):
        '''
        Return a tuple of state:
            number of active switches in state
            sequence (string)
            unique and sorted sequence (string)
            command state list (array)
        '''
        return (sum(1 for state in self.command if state == True),
                self.sequence,
                ''.join(sorted(set(self.sequence))), # Unique and sorted
                self.command)

    def processInput(self):
        '''
        Read input until an EXECUTE command is found
        or the quit character is found
        '''
        self.clearState()
        ch = ''
        lastch = ''
        while(True):
            ch = self.readChar()
            if ch == self.quitChar:
                return False

            if ch == lastch:
                continue    # Key repeats should be ignored
            else:
                lastch = ch

            if ord(ch) == self.EXECUTE_KEY:
                return True
            else:
               self.updateState(ch)
               
############################################################
# MAIN
############################################################
if __name__ == '__main__':

    # Index number of array corresponds to switch number. There are extra files in list (more than 41)
    # A file exists at 0 as a place holder, it is loaded and must exist
    # but it is not ever used since there is now switch 0
    effectFiles = [
        # NASA sounds come from https://soundcloud.com/nasa
        'sounds/569462main_eagle_has_landed.mp3', # Place holder only
        'sounds/582369main_Mercury-4_Clock-Started.mp3',
        'sounds/582368main_Mercury-6_God-Speed.mp3',
        'sounds/582367main_Mercury-6_Zero-G.mp3',
        'sounds/582371main_Aurora-7_Liftoff.mp3',
        'sounds/582374main_Aurora-7_Fireflies.mp3',
        'sounds/590320main_ringtone_apollo11_countdown.mp3',
        'sounds/569462main_eagle_has_landed.mp3',
        'sounds/590331main_ringtone_smallStep.mp3',
        'sounds/574928main_houston_problem.mp3',
        'sounds/586447main_JFKwechoosemoonspeech.mp3',
        'sounds/591240main_JFKmoonspeech.mp3',
        'sounds/640148main_APU Shutdown.mp3',
        'sounds/640149main_Computers are in Control.mp3',
        'sounds/663784main_SLS_Audio_D.mp3',
        'sounds/578626main_sputnik-beep.mp3',
        'sounds/578628main_hskquindar.mp3',
        'sounds/578629main_hawquindar.mp3',
        'sounds/590189main_ringtone_131_launchNats.mp3',
        'sounds/590318main_ringtone_135_launch.mp3',
        'sounds/640165main_Lookin At It.mp3',
        'sounds/640166main_MECO.mp3',
        # From: https://archive.org/details/Apollo11Audio
        # and https://archive.org/details/apolloaudiocollection
        # https://archive.org/details/nasaaudiocollection&tab=about
        'sounds/Apollo11-gonogo_for_powered_decent.wav',
        'sounds/Apollo11-GoNoGo-for-landing.wav',
        'sounds/Apollo11-1201-alarm.wav',
        'sounds/Apollo11-1202-alarm.wav',
        'sounds/Apollo11-keep-chatter-down.wav',
        'sounds/Apollo11-only-callouts-are-fuel.wav',
        'sounds/Apollo11-stay-no-stay.wav',
        # http://www.trekcore.com/audio/
        'sounds/autodestructsequencearmed_ep.mp3',
        'sounds/computer_error.mp3',
        'sounds/computer_work_beep.mp3',
        'sounds/computerbeep_2.mp3',
        'sounds/consolewarning.mp3',
        'sounds/input_ok_3_clean.mp3',
        'sounds/tos_bridge_1_activate.mp3',
        'sounds/tos_destructsequence_ep.mp3',
        'sounds/tos_hailing_frequencies_open.mp3',
        'sounds/console_explo_01.mp3',
        'sounds/tng_torpedo2_clean.mp3',
        'sounds/tos_main_viewing_screen.mp3',
        ]

    def stopPreviousSoundEffect():
        ''' KLR Put this in soundeffects.py and put into a class that make
        keeps track of what's playing instead of this '''
        for i in range(len(se)):    # Brute force way to stop previous sounds without having to remember what was playing
            se[i].stop()

    def keyAction(ch):
        idx = mapCharToSwitchNumber(ch)
        print '[S%.2d] ' % (idx),
        if ch in string.printable:
            print " '" + ch + "'",
        else:
            print "not printable",
        print ord(ch)

        stopPreviousSoundEffect()
        se[idx].play()


    # Initialize all sounds effects by loading into memory
    se = []
    for fn in effectFiles:
        se.append(SoundEffect(fn))

    smek = SMEK(quitChar='Q', keyHandler=keyAction)

    while(smek.processInput()):
        (actives, seq, uniq, command) = smek.getState()
        # EXECUTE will return 0 actives after the first press and while it is being
        # scanned before it is released. The caller should just ignore if actives == 0
        stopPreviousSoundEffect()
        # KLR I could play an EXECUTE sound here if desired
        if actives > 0:
            print ''
            print 'Sequence: ' + seq
            print 'Sorted:   ' + uniq
            print 'Active switches: ' + str(actives)
            print 'Command: '
            #print command
            for row in range(5):
                for col in range(8):
                    sw = 5*col + 1 + row
                    if sw == 39:
                        print '[EXEC]',
                    elif sw == 40:
                        print '[CLR ]',
                    elif command[sw]:
                        print '[S%.2d]' % (sw),
                    else:
                        print '[---]',
                print ''
