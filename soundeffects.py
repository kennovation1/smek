from AppKit import NSSound
from time import sleep

'''
Rough class to play and audio file
Probably better ways of doing this using PyGame or something else
but I already loaded AppKit (needed to pip install PyObjC) and this kinda of works
'''
class SoundEffect():
    def __init__(self, soundFile):
        self.sound = NSSound.alloc()
        try:
            self.sound.initWithContentsOfFile_byReference_(soundFile, True)
        except:
            print 'Error opening sound file: ' + soundFile

    def stop(self):
        self.sound.stop()

    def play(self, sync = False):
        '''
        Play the audio associated with this object.
        If sync is True wait for the entire file to be played.
        '''
        self.sound.stop()
        try:
            self.sound.play()
            if sync:
                sleep(self.sound.duration())
                self.sound.stop()
        except:
            print 'Error playing sound'


############################################################
# MAIN
############################################################
if __name__ == '__main__':

    effectFile = 'sounds/569462main_eagle_has_landed.mp3'
    se = SoundEffect(effectFile)
    for i in range(3):
        print 'Started playing ' + str(i)
        se.play(sync=True)
        print 'Done.'
