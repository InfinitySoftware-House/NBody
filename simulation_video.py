# Copyright 2021 Google LLC
# SPDX-License-Identifier: Apache-2.0
# https://www.apache.org/licenses/LICENSE-2.0

import pygame,sys,os,datetime

class Video:

    def __init__(self, path):
        self.path = path
        self.name = "capture"
        self.cnt = 0

        # Ensure we have somewhere for the frames
        try:
            os.makedirs(self.path)
        except OSError:
            pass
    
    def make_png(self,screen):
        self.cnt+=1
        fullpath = os.path.join(self.path, self.name + "%08d.png"%self.cnt)
        pygame.image.save(screen,fullpath)

    #https://stackoverflow.com/questions/44947505/how-to-make-a-movie-out-of-images-in-python
    #https://stackoverflow.com/questions/3561715/using-ffmpeg-to-encode-a-high-quality-video
    def make_mp4(self):
        fullpath = os.path.join(self.path, self.name + "%08d.png")
        bash = f"ffmpeg -r 60 -i {fullpath} -vcodec mpeg4 -q:v 0 -y movie_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
        os.system(bash)

# if __name__  == '__main__':
#     video = Video()
#     video.make_mp4()