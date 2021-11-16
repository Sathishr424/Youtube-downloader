import pygame,os,time
from tkinter import *
from pytube import YouTube, Playlist, Channel
from urllib.request import urlopen
import io,threading,subprocess
import json

h_display = 600
v_display = 600

white = (255, 255, 255)
black = (0,0,0)
gray = (128, 128, 128)
green = (0, 255, 128)
red = (255, 64, 64)

BG = (147, 51, 230) #LIGHT_PINK
#BG = (149, 233, 175) #LIGHT_GREEN
#BG = (233, 185, 185) #LIGHT_RED
IN_BOX = (30,30,30)
#BTN_COLOR = (BG[0]+18,BG[1]+22,BG[2]+9)
#BTN_PRESSED_COLOR = (BTN_COLOR[0]-55,BTN_COLOR[1]-65,BTN_COLOR[2]-23)
THEME = ['pink',0]
AV_THEMES = ""
SCROLL_BAR, SCROLL_BAR_LINE, SCROLL_BAR_BODY, TXT_COLOR, CONTAINER_COLOR, BACKGROUND, BTN_COLOR, BTN_PRESSED_COLOR = [],[],[],[],[],[],[],[]
def loadTheme():
    global AV_THEMES, SCROLL_BAR, SCROLL_BAR_LINE, SCROLL_BAR_BODY, TXT_COLOR, CONTAINER_COLOR, BACKGROUND, BTN_COLOR, BTN_PRESSED_COLOR, THEME
    THEME = ['pink',0]
    with open('theme.ini', 'r') as file:
        AV_THEMES = json.loads(file.read())
        for i in range(len(AV_THEMES)):
            if i == THEME[1]:
                THEME[1] = i
                THEME[0] = AV_THEMES[THEME[1]]['name']
                clr = AV_THEMES[i]['color']
                SCROLL_BAR = clr[0]
                SCROLL_BAR_LINE = clr[1]
                SCROLL_BAR_BODY = clr[2]
                TXT_COLOR = clr[3]
                CONTAINER_COLOR = clr[4]
                BACKGROUND = clr[5]
                BTN_COLOR = clr[6]
                BTN_PRESSED_COLOR = clr[7]

def switchTheme(mode):
    global AV_THEMES, SCROLL_BAR, SCROLL_BAR_LINE, SCROLL_BAR_BODY, TXT_COLOR, CONTAINER_COLOR, BACKGROUND, BTN_COLOR, BTN_PRESSED_COLOR, THEME
    if mode == 'next':
        if THEME[1]+1 < len(AV_THEMES):
            THEME[1]+=1
        else:
            THEME[1] = 0
    elif mode == 'prev':
        if THEME[1]-1 >= 0:
            THEME[1]-=1
        else:
            THEME[1] = len(AV_THEMES)-1        
    THEME[0] = AV_THEMES[THEME[1]]['name']
    clr = AV_THEMES[THEME[1]]['color']
    SCROLL_BAR = clr[0]
    SCROLL_BAR_LINE = clr[1]
    SCROLL_BAR_BODY = clr[2]
    TXT_COLOR = clr[3]
    CONTAINER_COLOR = clr[4]
    BACKGROUND = clr[5]
    BTN_COLOR = clr[6]
    BTN_PRESSED_COLOR = clr[7]    
            
#SCROLL_BAR = (139,141,143)
#SCROLL_BAR_LINE = (86,88,89)
#SCROLL_BAR_BODY = (86,88,89)
#TXT_COLOR = white
##PROGRESS_BAR = (43,194,83)
#CONTAINER_COLOR = (63,72,82)
#BACKGROUND = (39,44,51)
#BTN_COLOR = (165,73,239)
#BTN_PRESSED_COLOR = (110,8,216)

DOWNLOAD_TYPE = ['video','720p','360p']

def renderText(txt, pos, size, fnt, bold, txtColor, center=False):
    font = pygame.font.SysFont(fnt, size, bold)
    try:
        text = font.render(txt, True, txtColor)
    except:
        text = font.render("VIDEO_NAME_NOT_SUPPORTED", True, txtColor)
    rect = text.get_rect()
    rect.center = pos
    if not center:
        rect.left = pos[0]
        rect.top = pos[1]
    #pygame.draw.rect(gameDisplay, bgColor, [int(rect.left-(size/2)), int(rect.top-(size/2)), rect.width+size, rect.height+size])
    gameDisplay.blit(text, rect)

def getTextRectSize(txt, pos, size, fnt, bold, txtColor, center=False):
    font = pygame.font.SysFont(fnt, size, bold)
    text = font.render(txt, True, txtColor)
    rect = text.get_rect()
    rect.center = pos
    #print(rect.left, rect.top, rect.width, rect.height)
    if not center:
        rect.left = pos[0]
        rect.top = pos[1]
    #print(rect.left, rect.top, rect.width, rect.height)
    return [rect.left-(size/2), rect.top-(size/2), rect.width+size, rect.height+size]

class Rectangle:
    def __init__(self,pos,size,color,name='rect'):
        self.pos = pos
        self.size = size
        self.name = name
        self.color = color
        self.type = 'Rect'
    
    def render(self):
        pygame.draw.rect(gameDisplay, self.color, [self.pos[0],self.pos[1],self.size[0],self.size[1]])
    
    def update(self,mouse,click):
        if mouse[0] > self.pos[0] and mouse[0] < self.pos[0]+self.size and \
           mouse[1] > self.pos[1] and mouse[1] < self.pos[1]+self.size:
            return True

class Button_:
    def __init__(self, name, pos, txtSize, font):
        self.name = name
        self.pos = pos
        self.txtSize = txtSize
        self.collision = False
        self.type = 'Btn'
        self.font = font
        self.rect = self.getTextRectSize(self.name, self.pos, self.txtSize, font, False, black, (206,198,235), False)
    
    def updatePos(self,pos):
        self.pos = pos
        self.rect = self.getTextRectSize(self.name, self.pos, self.txtSize, self.font, False, black, (206,198,235), False)
        
    def render(self):
        if self.collision: self.renderTextWithRectangle(self.name, self.pos, self.txtSize, self.font , False, white, BTN_PRESSED_COLOR, False)
        else: self.renderTextWithRectangle(self.name, self.pos, self.txtSize, self.font , False, white, BTN_COLOR, False)
    
    def getTextRectSize(self,txt, pos, size, fnt, bold, txtColor, bgColor, center=True):
        font = pygame.font.SysFont(fnt, size, bold)
        text = font.render(txt, True, txtColor)
        rect = text.get_rect()
        rect.center = pos
        #print(rect.left, rect.top, rect.width, rect.height)
        if not center:
            rect.left = pos[0]
            rect.top = pos[1]
        #print(rect.left, rect.top, rect.width, rect.height)
        return [rect.left-(size/2), rect.top-(size/2), rect.width+size, rect.height+size]

    def renderTextWithRectangle(self,txt, pos, size, fnt, bold, txtColor, bgColor, center=True):
        font = pygame.font.SysFont(fnt, size, bold)
        text = font.render(txt, True, txtColor)
        rect = text.get_rect()
        rect.center = pos
        if not center:
            rect.left = pos[0]
            rect.top = pos[1]
        pygame.draw.rect(gameDisplay, bgColor, [int(rect.left-(size/2)), int(rect.top-(size/2)), rect.width+size, rect.height+size])
        gameDisplay.blit(text, rect)    
    
    def update(self):
        mouse = pygame.mouse.get_pos(); click = pygame.mouse.get_pressed()
        if mouse[0] > self.rect[0] and mouse[0] < self.rect[0]+self.rect[2] and \
           mouse[1] > self.rect[1] and mouse[1] < self.rect[1]+self.rect[3]:
            self.collision = True
            if click[0] == 1: 
                time.sleep(0.1)
                return 1
            if click[2] == 1:
                time.sleep(0.1)
                return 2
        else: self.collision = False
        return 0

class ScrollBar:
    def __init__(self,size):
        self.size = size
        print(size)
        self.currentPos = 0
        self.barPos = 30
        self.click = False
        self.clickPos = [0,0]
        self.diff = (v_display-3) - 31
        self.barSize = (self.diff*2)//(self.size-7)
        print(self.diff, self.barSize)
    
    def render(self):
        pygame.draw.rect(gameDisplay, SCROLL_BAR_BODY, [h_display-20,11,18,v_display-1])
        #pygame.draw.rect(gameDisplay, gray, [h_display-3,10,1,v_display-30]) 
        
        pygame.draw.rect(gameDisplay, SCROLL_BAR_LINE, [h_display-20,10,18,20])
        pygame.draw.rect(gameDisplay, SCROLL_BAR_LINE, [h_display-20,v_display-25,18,20])
        pygame.draw.rect(gameDisplay, SCROLL_BAR, [h_display-20,self.barPos,18,self.barSize])
        
    
    def update(self):
        mouse = pygame.mouse.get_pos(); click = pygame.mouse.get_pressed()
        if self.click:
            #print("CLICK")
            if mouse[1] - self.clickPos < 30:
                self.barPos = 30
            elif mouse[1] - self.clickPos > (v_display-25)-self.barSize:
                self.barPos = (v_display-25)-self.barSize
            else:
                self.barPos = mouse[1] - self.clickPos
            self.currentPos = int((self.barPos-30) / (self.diff/self.size))
            print(self.currentPos)
            
        if mouse[0] >= h_display-20 and mouse[1] >= self.barPos and mouse[1] <= self.barPos+self.barSize:
            if click[0] == 1:
                if not self.click:
                    #print("FIRST")
                    self.clickPos = mouse[1] - self.barPos
                    self.click = True
            elif click[0] == 0: self.click = False
        elif click[0] == 0: self.click = False
        
        if mouse[0] >= h_display-20 and mouse[1] >= 10 and mouse[1] <= 30 and click[0] == 1:
            if self.currentPos >= 1: self.currentPos -= 1
            self.barPos = int(self.currentPos * (self.diff/self.size)) + 30
        elif mouse[0] >= h_display-20 and mouse[1] >= v_display-25 and mouse[1] <= v_display-5 and click[0] == 1:
            if self.currentPos < self.size-4: self.currentPos += 1
            self.barPos = int(self.currentPos * (self.diff/self.size)) + 30
    
    def scrollDown(self):
        if self.currentPos >= 1: 
            self.currentPos -= 1
            self.barPos = int(self.currentPos * (self.diff/self.size)) + 30
            
    def scrollUp(self):
        if self.currentPos < self.size-4: 
            self.currentPos += 1
            self.barPos = int(self.currentPos * (self.diff/self.size)) + 30            
        
class Handler:
    def __init__(self,renderable,playlist, btns):
        self.renderable = renderable
        self.scroll = ScrollBar(len(self.renderable))
        self.start = 0
        self.btns = btns
        self.btns[-1].name = "Download All (" + str(len(self.renderable)) + ")"
        self.downloading = False

    def render(self):
        if len(self.renderable) > 7: self.scroll.render()
        for i in range(self.start, self.start+7):
            if i < len(self.renderable):
                self.renderable[i].render()
        for btn in self.btns:
            btn.render()
    
    def update(self):
        if self.downloading:
            finish = True
            for yt in self.renderable:
                if yt.isDownloading:
                    finish = False
                    break
                elif not yt.finished:
                    yt.downloadYT()
                    yt.isDownloading = True
                    finish = False
            if finish:
                self.downloading = False
                self.btns[-1].name = 'Downloaded'
                    
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        for btn in self.btns:
            if btn.update() == 2:
                if btn.name.find("THEME") != -1:
                    switchTheme('prev')
                    btn.name = "THEME: " + THEME[0]                
            if btn.update() == 1:
                if btn.name == 'VIDEO':
                    btn.name = 'AUDIO'
                    DOWNLOAD_TYPE[0] = 'audio'
                elif btn.name == 'AUDIO':
                    btn.name = 'VIDEO'
                    DOWNLOAD_TYPE[0] = 'video'
                elif btn.name == '720p':
                    btn.name = '360p'
                    DOWNLOAD_TYPE[1] = '360p'
                elif btn.name == '360p':
                    btn.name = '720p'
                    DOWNLOAD_TYPE[1] = '720p'
                elif btn.name.find("THEME") != -1:
                    switchTheme('next')
                    btn.name = "THEME: " + THEME[0]
                elif btn.name.find('Download All') != -1:
                    btn.name = 'Downloading...'
                    self.downloading = True
        if len(self.renderable) > 7: 
            self.scroll.update()
            if self.start != self.scroll.currentPos:
                self.start = self.scroll.currentPos
                for i in range(self.start, self.start+7):
                    if i < len(self.renderable):
                        self.renderable[i].updatePos([2,((i-self.start)*81)+30])

class YoutubeDownloader:
    def __init__(self,root):
        self.root = root
        self.root.title("Youtube Downloader")
        self.root.resizable(False,False)
        icon = PhotoImage(file='icon.png')
        self.root.iconphoto(False,icon)
        main = LabelFrame(self.root,highlightthickness=2,highlightcolor='gray', text='Video | Playlist link', font='constantia 11')
        main.pack(pady=2,padx=2)
        #Label(main,text='Youtube',font='constantia 11').pack(anchor='w')
        self.link = Entry(main, width=70, font='constantia 11')
        self.link.pack(padx=5,pady=2)
        btnFrame = Frame(main)
        btnFrame.pack(anchor='w')
        Button(btnFrame, text='Single Video', font='constantia 10', command=lambda: self.start(self.link.get(), 0)).pack(side='left',pady=2,padx=5, anchor='w')
        Button(btnFrame, text='Playlist', font='constantia 10', command=lambda: self.start(self.link.get(), 1)).pack(side='left',pady=2,padx=5, anchor='w')
        Button(btnFrame, text='Channel', font='constantia 10', command=lambda: self.start(self.link.get(), 2)).pack(side='left',pady=2,padx=5, anchor='w')
        self.root.mainloop()
    
    def start(self,link,playlist):
        loadTheme()
        t = threading.Thread(target=pGame, args=(link,playlist))
        t.setDaemon(True)
        t.start()

class videoContainer:
    def __init__(self,pos,link):
        self.link = link
        self.yt = YouTube(link)
        self.yt.register_on_complete_callback(self.complete_function)
        self.yt.register_on_progress_callback(self.progress_function)
        self.pos = pos
        self.isDownloading = False
        self.type = 'mp4'
        self.progressWidth = (h_display-60) - (self.pos[0]+107)
        self.downloaded = 0
        self.stream = None
        self.finished = False
        self.filePath = ''
        self.size = 0
        self.thread = None
        vid = self.yt.vid_info['player_response']
        self.downloadText = '0 kb / 0 kb'
        self.img = pygame.image.load(io.BytesIO(urlopen(self.yt.thumbnail_url).read()))
        #self.img = pygame.image.load(io.BytesIO(urlopen((vid[vid.find('thumbnails')+len('thumbnails":[{"url":"'):vid.find('default.jpg"')+len('default.jpg')])).read()))
        #self.img = pygame.image.load("jotaro.jpg")
        self.img = pygame.transform.scale(self.img, (100,75))
        self.btn = Button_('Download',(h_display-150,self.pos[1]+30),13,'Times')
    
    def shortTitle(self,st):
        if len(st) > 60:
            return st[:61] + "....."
        return st
    
    def updatePos(self,pos):
        self.pos = pos
        self.btn.updatePos((self.pos[0]+160,self.pos[1]+30))
    
    def complete_function(self, stream, file_path):
        self.finished = True
        self.isDownloading = False
        self.filePath = file_path
    
    def progress_function(self, stream, chunk, bytes_remaining):
        remaining = (100 * bytes_remaining) / self.size
        self.downloadText = str(round(((self.size/1024)-int(bytes_remaining/1024))/1024,2)) +  " MB / " + str(round((self.size/1024)/1024,2)) + " MB"
        self.downloaded = 100 - int(remaining)
        #print(self.downloaded, self.downloadText)
    
    def viewsConverter(self, view):
        if view < 1000:
            return str(view) + " views |"
        elif view < 1000000:
            return str(round(view/1000,1)) + "K views |"
        elif view < 1000000000:
            return str(round(view/1000000,1)) + "M views |"
        else:
            return str(round(view/1000000000,2)) + "B views |"
        
    def getTime(self,tme):
        minute = str(int(tme / 60))
        sec = str(tme - (int(tme / 60) * 60))
        if len(sec) == 1: sec = "0" + sec
        if len(minute) == 1: minute = "0" + minute
        return str(minute) + ":" + str(sec)    

    def render(self):
        pygame.draw.rect(gameDisplay, CONTAINER_COLOR, [self.pos[0],self.pos[1],h_display-25,80])
        gameDisplay.blit(self.img, (self.pos[0]+2,self.pos[1]+2))
        renderText(self.shortTitle(self.yt.title), (self.pos[0]+107, self.pos[1]+4), 15, 'Times', False, TXT_COLOR)
        #renderText(self.shortTitle(self.link), (self.pos[0]+2, self.pos[1]+4), 14, 'Times', False, black)
        self.btn.updatePos([self.pos[0]+115, self.pos[1]+30])
        pos = getTextRectSize(self.getTime(self.yt.length) + " |", (self.btn.rect[0]+self.btn.rect[2]+20, self.pos[1]+27), 15, 'Times', False, TXT_COLOR)
        renderText(self.getTime(self.yt.length) + " |", (pos[0], self.pos[1]+27), 15, 'Times', False, TXT_COLOR)
        pos = getTextRectSize(self.viewsConverter(self.yt.views), (pos[0]+pos[2], self.pos[1]+27), 15, 'Times', False, TXT_COLOR)
        renderText(self.viewsConverter(self.yt.views), (pos[0], self.pos[1]+27), 15, 'Times', False, TXT_COLOR)
        if self.btn.name == ' Open  ':
            self.btn.render()
            if self.btn.update():
                #print('start vlc "'+self.filePath+'"')
                os.system('start vlc "'+self.filePath+'"')
        if not self.isDownloading and not self.finished:
            self.btn.render()
            if self.btn.update(): 
                self.isDownloading = True
                self.downloadYT()
        elif not self.finished:
            pygame.draw.line(gameDisplay, BTN_PRESSED_COLOR, (self.pos[0]+107, self.pos[1]+50), (h_display-60, self.pos[1]+50), 1)
            pygame.draw.line(gameDisplay, BTN_PRESSED_COLOR, (self.pos[0]+107, self.pos[1]+60), (h_display-60, self.pos[1]+60), 1)

            pygame.draw.line(gameDisplay, BTN_PRESSED_COLOR, (self.pos[0]+107, self.pos[1]+50), (self.pos[0]+107, self.pos[1]+60), 1) 
            pygame.draw.line(gameDisplay, BTN_PRESSED_COLOR, (h_display-60, self.pos[1]+50), (h_display-60, self.pos[1]+60), 1)           
            pygame.draw.rect(gameDisplay, BTN_COLOR, [self.pos[0]+108, self.pos[1]+51, int(self.progressWidth*(self.downloaded/100)), 8])
            
            renderText(str(self.downloaded) + '%', (h_display-55, self.pos[1]+50), 12, 'Times', False, TXT_COLOR)
            renderText(self.downloadText, (self.pos[0]+107, self.pos[1]+65), 12, 'Times', False, TXT_COLOR)
        else:
            self.btn.name = ' Open  '
            #Button_('Download Finished!',(self.btn.rect[0]+self.btn.rect[3]+15,self.pos[1]+27),13,'Times').render()
    
    def downloadYT(self):
        if DOWNLOAD_TYPE[0] == 'audio':
            self.type = 'webm'
            self.stream = self.yt.streams.filter(type='audio')[0]
            self.size = self.stream.filesize
            self.thread = threading.Thread(target=self.stream.download, args=('Downloads',))
            #t.daemon = True
            self.thread.setDaemon(True)
            self.thread.start()
        elif DOWNLOAD_TYPE[0] == 'video':
            self.type = 'mp4'
            try:
                self.stream = self.yt.streams.get_by_resolution(DOWNLOAD_TYPE[1])
                self.size = self.stream.filesize
                self.thread = threading.Thread(target=self.stream.download, args=('Downloads',))
                #t.daemon = True
                self.thread.setDaemon(True)
                self.thread.start()
                #self.stream.download("Downloads")
            except:
                self.stream = self.yt.streams.get_by_resolution(DOWNLOAD_TYPE[2])
                self.size = self.stream.filesize
                self.thread = threading.Thread(target=self.stream.download, args=('Downloads',))
                #t.daemon = True
                self.thread.setDaemon(True)
                self.thread.start()
                #self.stream.download("Downloads")             

def startFun(link,playlist):
    global handler
    renderable = []
    if playlist == 1:
        p = Playlist(link)
        urls = p.video_urls
        for i in range(len(urls)):
            renderable.append(videoContainer([2,(i*81)+30],urls[i]))
    elif playlist == 2:
        p = Channel(link)
        urls = p.video_urls
        for i in range(len(urls)):
            renderable.append(videoContainer([2,(i*81)+30],urls[i]))
    else:
        renderable.append(videoContainer([2,30],link))
    
    typeBtn = Button_("VIDEO", (7,7), 13, "Times")
    qualityBtn = Button_("720p", (typeBtn.rect[0]+typeBtn.rect[2]+15,7), 13, "Times")
    
    downloadAll = Button_("Download All", (qualityBtn.rect[0]+qualityBtn.rect[2]+25,7), 13, "Times")
    themeBtn = Button_("THEME: " + THEME[0], (downloadAll.rect[0]+downloadAll.rect[2]+50,7), 13, "Times")
    
    btns = [typeBtn, qualityBtn, themeBtn, downloadAll]

    handler = Handler(renderable,playlist,btns)
        
def pGame(link,playlist):
    global gameDisplay, handler
    handler = None
    pygame.init()
    box = [h_display, v_display]
    clock = pygame.time.Clock()
    gameDisplay = pygame.display.set_mode((h_display, v_display))
    lastPos = 0
    size = 10
    pygame.display.set_caption("Youtube Download Manager..")
    icon = pygame.image.load("icon.png")
    pygame.display.set_icon(icon)
    
    top = Rectangle([5,5],[h_display-10,40],BTN_COLOR)
    main = Rectangle([5,50],[h_display-10,v_display-55],BTN_COLOR)
    
    t = threading.Thread(target=startFun, args=(link,playlist,))
    
    t.start()
    
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                quit()
            if e.type == pygame.MOUSEBUTTONDOWN:
                if e.button == 4:
                    handler.scroll.scrollDown()
                elif e.button == 5:
                    handler.scroll.scrollUp()
                    
        gameDisplay.fill( BACKGROUND )
        if not t.is_alive():
            handler.render()
            handler.update()
        else:
            renderText("Loading please wait....", (h_display//2, v_display//2), 20, 'Times', False, TXT_COLOR, True)
        pygame.display.update()

if __name__ == '__main__':
    YoutubeDownloader(Tk())
    #pGame("https://www.youtube.com/playlist?list=PLgWBVkaukvyZ826OWSm8-L936YAlpVlBN", True)
    #yt = YouTube("https://www.youtube.com/watch?v=XbhecuoEgxs")
    #vid = yt.vid_info['player_response']
    #print(vid[vid.find('thumbnails')+len('thumbnails":[{"url":"'):vid.find('default.jpg"')+len('default.jpg')])
    #print("NOTHING")
