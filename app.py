import spacy
from flask import Flask, request, jsonify, render_template
nlp = spacy.load('en_core_web_sm')
app = Flask(__name__, static_url_path='/static', template_folder='templates')


@app.route("/", methods=["GET"])
def root():
    return render_template('index.html')


@app.route("/get_tosv_sentence", methods=["POST"])
def get_tosv_sentence():
    s = request.get_json()
    return jsonify(get_tokens(nlp(s)))


def _print_tokens(doc):
    for token in doc:
        print("txt={:15s}\tlemma={:10s}\tpos={:10s}\ttag={:10s}\t\tdep={}".format(
            token.text, token.lemma_, token.pos_, token.tag_, token.dep_))
    print()


def _append_token_before_adjs(t, key, token, adjs):
    t[key].append(token.text)
    while adjs:
        t[key].append(adjs.pop(0))


def get_tokens(doc):
    sentences = list()
    t = None
    # adjectives go after subjects or objects
    adjs = []
    be_verbs = ['am', 'is', 'are', 'were', 'was', 'be', 'will']
    for token in doc:
        if not t:
            t = dict(
                verbs=[],
                subjects=[],
                objects=[],
                times=[]
            )
        token_pos = token.pos_
        token_text = token.text.lower()
        if token_pos == 'VERB':
            # 'to be' verbs are not used in ASL
            if token_text in be_verbs or "'" in token_text:
                continue
            t['verbs'].append(token_text)
        elif token_pos == 'NOUN':
            if token.dep_ == 'npadvmod':
                _append_token_before_adjs(t, 'times', token, adjs)
            else:
                _append_token_before_adjs(t, 'objects', token, adjs)
        elif token_pos == 'PRON':
            if token.dep_ == 'npadvmod':
                _append_token_before_adjs(t, 'times', token, adjs)
            elif not t['subjects']:
                # just append first subject
                _append_token_before_adjs(t, 'subjects', token, adjs)
        elif token_pos == 'ADJ':
            adjs.append(token_text)
        elif token_pos == 'PUNCT' or token_text is 'then':
            if t['verbs'] and t['subjects']:
                sentences.append(t)
                t = None
    if t:
        sentences.append(t)
    return sentences


if __name__ == "__main__":
    app.run()
