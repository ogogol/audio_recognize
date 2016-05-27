
from bs4 import BeautifulSoup

def readSoup(filename, type = 'lxml'):
    f = open(filename, 'r')
    xml = f.read()
    f.close()
    soup = BeautifulSoup(xml, type)

    return soup

def writeSoup(filename, soup):
    f = open(filename, 'w')
    f.write(soup.prettify())
    f.close()

    return

def addLabelTrackTag(filename_aup, numlabels = 100):

    soup = readSoup(filename_aup)
    tag = soup.wavetrack
    new_tag = soup.new_tag('labeltrack')
    new_tag['name'] = "Label track"
    new_tag['numlabels'] = "%s" % numlabels
    new_tag['height'] = "408"
    new_tag['minimized'] = "0"
    tag.insert_after(new_tag)

    soup.html.body.unwrap()
    soup.html.unwrap()
    soup.tags.unwrap()
    writeSoup(filename_aup, soup)

    soup = readSoup(filename_aup, "xml")
    tag = soup.wavetrack
    new_tag = soup.new_tag('tags')
    tag.insert_before(new_tag)
    writeSoup(filename_aup, soup)

    return soup

def addLabelTrack(soup, t, t1, label):
    tag = soup.labeltrack
    new_tag = soup.new_tag('label')
    new_tag['t'] = "%s" % t
    new_tag['t1'] = "%s" % t1
    new_tag['title'] = "%s" % label
    tag.append(new_tag)

    return soup

def writeLabelTracks_file(filename, chunks_range):

    numlabels = len(chunks_range)
    soup = addLabelTrackTag(filename, numlabels)
    for i, val in enumerate(chunks_range):
        soup = addLabelTrack(soup, val[0], val[1], i)

    writeSoup(filename,soup)

    return
