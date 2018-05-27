import spacy
from flask import Flask, request, jsonify, render_template
from bs4 import BeautifulSoup
import requests
from functools import reduce

nlp = spacy.load('en_core_web_sm')
app = Flask(__name__, static_url_path='/static', template_folder='templates')


@app.route("/", methods=["GET"])
def root():
    return render_template('index.html')


@app.route("/get_tosv_sentence", methods=["POST"])
def get_tosv_sentence():
    doc = nlp(request.get_json())
    sentences_data = get_sentences_with_videos(doc)
    # TODO maybe later return more videos for each pos
    sentences = \
        [
            dict(subjects=[t.text for t in s.subjects],
                 objects=[t.text for t in s.objects],
                 times=[t.text for t in s.times],
                 verbs=[t.text for t in s.verbs]
                 )
            for s in sentences_data
        ]
    videos = [
        [(t.text.capitalize(), t.video, t.source) for t in s.times] +
        [(t.lemma.capitalize(), t.video, t.source) for t in s.objects] +
        [(t.text.capitalize(), t.video, t.source) for t in s.subjects] +
        [(t.lemma.capitalize(), t.video, t.source) for t in s.verbs]
         for s in sentences_data
    ]
    videos = reduce(lambda x, y: x + y, videos) if videos else []
    videos = [v for v in videos if v[1]]
    return jsonify(dict(sentences=sentences, videos=videos))


def get_video_url(w):
    try:
        r = requests.get('https://www.signingsavvy.com/search/' + w.lower())
        soup = BeautifulSoup(r.content, 'html.parser')
        url = "https://www.signingsavvy.com/" + \
              [x for x in soup.find_all('a') if x.contents[0] == w.upper()][0].attrs[
                  'href']
        r = requests.get(url)
        soup = BeautifulSoup(r.content, 'html.parser')
        video_path = soup.find_all('video')[0].contents[0].attrs['src']
        video_url = 'https://www.signingsavvy.com/' + video_path
        return video_url, url
    except:
        return None, None


class PartOfSpeech:
    VERB = 1
    OBJECT = 2
    SUBJECT = 3
    TIME = 4
    MOD = 5


class Token:
    def __init__(self, text, lemma, pos):
        self.part_of_speech = pos
        self.text = text
        self.lemma = lemma  # use to find videos for objects and verbs
        text = lemma if pos is PartOfSpeech.OBJECT or pos is PartOfSpeech.VERB else text
        self.video, self.source = get_video_url(text)


class Sentence:
    def __init__(self):
        self.verbs = list()
        self.subjects = list()
        self.objects = list()
        self.times = list()

    def add_word(self, pos, token, adjs):
        word_list = None
        if pos == PartOfSpeech.VERB:
            word_list = self.verbs
        if pos == PartOfSpeech.SUBJECT:
            word_list = self.subjects
        if pos == PartOfSpeech.OBJECT:
            word_list = self.objects
        if pos == PartOfSpeech.TIME:
            word_list = self.times
        word_list.append(Token(text=token.text, lemma=token.lemma_, pos=pos))
        while adjs:
            word_list.append(adjs.pop(0))


def get_sentences_with_videos(doc):
    sentences = list()
    sentence = None
    # adjectives go after subjects or objects
    adjs = []

    for token in doc:
        if not sentence:
            sentence = Sentence()
        token_pos = token.pos_
        if token_pos == 'VERB':
            # 'to be' verbs are not used in ASL
            if token.lemma_ == 'be':
                continue
            sentence.add_word(PartOfSpeech.VERB, token, adjs)
        elif token_pos == 'NOUN':
            if token.dep_ == 'npadvmod':        # modifiers are adjectives
                sentence.add_word(PartOfSpeech.TIME, token, adjs)
            else:
                sentence.add_word(PartOfSpeech.OBJECT, token, adjs)
        elif token_pos == 'PRON':
            if token.dep_ == 'npadvmod':
                sentence.add_word(PartOfSpeech.TIME, token, adjs)
            elif not sentence.subjects:         # just append first subject
                sentence.add_word(PartOfSpeech.SUBJECT, token, adjs)
        elif token_pos == 'ADJ':
            adjs.append(Token(text=token.text, lemma=token.lemma_, pos=PartOfSpeech.MOD))
        elif token_pos == 'PUNCT' or token.text is 'then':  # new sentence
            if sentence.verbs and (sentence.objects or sentence.subjects):
                sentences.append(sentence)
                adjs = None
                sentence = None
    if sentence.verbs and (sentence.objects or sentence.subjects):
        sentences.append(sentence)
    return sentences


if __name__ == "__main__":
    app.run()
