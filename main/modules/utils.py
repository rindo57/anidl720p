from math import floor
import os
from main import queue
import cv2, random
from string import ascii_letters, ascii_uppercase, digits
from pyrogram.types import Message, MessageEntity

def get_duration(file):
    data = cv2.VideoCapture(file)
  
    frames = data.get(cv2.CAP_PROP_FRAME_COUNT)
    fps = int(data.get(cv2.CAP_PROP_FPS))
    seconds = int(frames / fps)
    return seconds

def get_screenshot(file):
    cap = cv2.VideoCapture(file)
    name = "./" + "".join(random.choices(ascii_uppercase + digits,k = 10)) + ".jpg"

    total_frames = round(cap.get(cv2.CAP_PROP_FRAME_COUNT))-1
    frame_num = random.randint(0,total_frames)
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num-1)
    res, frame = cap.read()

    cv2.imwrite(name, frame)
    cap.release()
    #cv2.destroyAllWindows()
    return name

def get_filesize(file):
    x = os.path.getsize(file)
    x = round(x/(1024*1024))
    if x > 1024:
        x = str(round(x/1024,2)) + " GB"
    else:
        x = str(x) + " MB"

    return x

def get_epnum(name):
    x = name.split(" - ")[-1].strip()
    x = x.split(" ")[0]
    x = x.strip()
    return x

def format_time(time):
    min = floor(time/60)
    sec = round(time-(min*60))

    time = str(min) + ":" + str(sec)
    return time

def format_text(text):
    ftext = ""
    for x in text:
        if x in ascii_letters or x == " " or x in digits:
            ftext += x
        else:
            ftext += " "
    
    while "  " in ftext:
        ftext = ftext.replace("  "," ")
    return ftext

def episode_linker(f,en,text,link):
    ent = en
    off = len(f) + 2
    length = len(text)
    new = MessageEntity(type="text_link",offset=off,length=length,url=link)
    ent.append(new)
    return ent

def tags_generator(title):
    x = "#" + title.replace(" ","_")
    
    while x[-1] == "_":
        x = x[:-1]
    return x

async def status_text(text):
    stat = """
⭐️ **Status :** {}

⏳ **Queue :** 

{}
"""
    
    queue_text = ""
    for i in queue:
        queue_text += "📌 " + i["title"].replace(".mkv","").replace(".mp4","").strip() + "\n"

    if queue_text == "":
        queue_text = "Nothing to encode here uwu"
        
    return stat.format(
        text,
        queue_text
    )


def get_progress_text(guessname,status,completed,speed,total,enco=False):
    text = """Name: {}
{}: {}%
[{}]
{} of {}
Speed: {}
ETA: {}
    """

    text2 = """{}
━━━━━━━━━━━━━━━━━━━━━
`Encoding to 720p HEVC 10Bit
Percentage: {}%
Speed: {}
ETA: {}`
    """

    if enco == False:
        total = str(total)
        completed = round(completed*100,2)
        size, forma = total.split(' ')
        if forma == "MiB":
            size = int(round(float(size)))
        elif forma == "GiB":
            size = int(round(float(size)*1024,2))

        percent = completed
        speed = round(float(speed)/1024) #kbps

        if speed == 0:
            speed = 0.1

        ETA = round((size - ((percent/100)*size))/(speed/1024))

        if ETA > 60:
            x = floor(ETA/60)
            y = ETA-(x*60)

            if x > 60:
                z = floor(x/60)
                x = x-(z*60)
                ETA = str(z) + " Hour " + str(x) + " Minute"
            else:
                ETA = str(x) + " Minute " + str(y) + " Second"
        else:
            ETA = str(ETA) + " Second"  

        if speed > 1024:
            speed = str(round(speed/1024)) + " MB"
        else:
            speed = str(speed) + " KB"

        completed = round((percent/100)*size)

        if completed > 1024:
            completed = str(round(completed/1024,2)) + " GB"
        else:
            completed = str(completed) + " MB"

        if size > 1024:
            size = str(round(size/1024,2)) + " GB"
        else:
            size = str(size) + " MB"

        fill = "🟩"
        blank = "🟥"
        bar = ""

        bar += round(percent/10)*fill
        bar += round(((20 - len(bar))/2))*blank


        speed += "/sec"
        text = text.format(
            name,
            status,
            percent,
            bar,
            completed,
            size,
            speed,
            ETA
        )
        return text

    elif enco == True:
        speed = float(speed)
        if speed == 0:
            speed = 0.01

        remaining = floor(int(total)-completed)
        ETA = floor(remaining/float(speed))

        if ETA > 60:
            x = floor(ETA/60)
            y = ETA-(x*60)

            if x > 60:
                z = floor(x/60)
                x = x-(z*60)
                ETA = str(z) + " Hour " + str(x) + " Minutes"
            else:
                ETA = str(x) + " Minutes " + str(y) + " Seconds"
        else:
            ETA = str(ETA) + " Seconds"

        percent = round((completed/total)*100)

        fill = "🟩"
        blank = "🟥"
        bar = ""

        bar += round(percent/10)*fill
        bar += round(((20 - len(bar))/2))*blank
        
        speed = str(speed) + "x"
  
        text2 = text2.format(
            guessname,
            percent,
            str(speed),
            ETA
        )
        return text2

async def gen_ss_sam(hash, fukpath, log):
    try:
        ss_path, sp_path = None, None
        os.mkdir(hash)
        tsec = await genss(fukpath)
        fps = 10 / tsec
        ncmd = f"ffmpeg -i '{fukpath}' -vf fps={fps} -vframes 10 '{hash}/pic%01d.png'"
        process = await asyncio.create_subprocess_shell(
            ncmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        await process.communicate()
        ss, dd = await duration_s(fukpath)
        __ = filename.split(".mkv")[-2]
        out = __ + "_sample.mkv"
        _ncmd = f'ffmpeg -i """{fukpath}""" -preset ultrafast -ss {ss} -to {dd} -c:v libx265 -crf 27 -map 0:v -c:a aac -map 0:a -c:s copy -map 0:s? """{out}""" -y'
        process = await asyncio.create_subprocess_shell(
            _ncmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        er = stderr.decode().strip()
        try:
            if er:
                if not os.path.exists(out) or os.path.getsize(out) == 0:
                    log.exception(str(er))
                    return (ss_path, sp_path)
        except BaseException:
            pass
        return hash, out
    except Exception as err:
        log.exception(str(err))
