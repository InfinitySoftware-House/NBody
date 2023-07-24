# Copyright 2021 Google LLC
# SPDX-License-Identifier: Apache-2.0
# https://www.apache.org/licenses/LICENSE-2.0

import pygame,os,datetime
import tempfile

class Video:
    def __init__(self):
        self.path = ""
        self.name = "capture"
        self.cnt = 0

        # Ensure we have somewhere for the frames
        self.temp_dir = tempfile.TemporaryDirectory()
        self.path = self.temp_dir.name
    
    def add_frame(self,screen):
        self.cnt+=1
        fullpath = os.path.join(self.path, self.name + "%08d.png"%self.cnt)
        pygame.image.save(screen,fullpath)

    #https://stackoverflow.com/questions/44947505/how-to-make-a-movie-out-of-images-in-python
    #https://stackoverflow.com/questions/3561715/using-ffmpeg-to-encode-a-high-quality-video
    def make_mp4(self):
        fullpath = os.path.join(self.path, self.name + "%08d.png")
        bash = f"ffmpeg -r 30 -i {fullpath} -vcodec mpeg4 -q:v 0 -y simulation_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
        os.system(bash)
        self.temp_dir.cleanup()

# if __name__  == '__main__':
#     video = Video()
#     video.make_mp4()