import spacy
from flask import Flask, request, jsonify
nlp = spacy.load('en_core_web_sm')
app = Flask(__name__)


def print_tokens(doc):
    for token in doc:
        print("txt={:15s}\tlemma={:10s}\tpos={:10s}\ttag={:10s}\t\tdep={}".format(
            token.text, token.lemma_, token.pos_, token.tag_, token.dep_))
    print()


def _append_token_before_adjs(t, key, token, adjs):
    t[key].append(token.text)
    while adjs:
        t[key].append(adjs.pop(0))


def get_tokens(doc):
    t = dict(
        verbs=[],
        subjects=[],
        objects=[],
        time=[]
    )
    # adjectives go after subjects or objects
    adjs = []
    for token in doc:
        if token.pos_ == 'VERB':
            t['verbs'].append(token.text)
        elif token.pos_ == 'NOUN':
            if token.dep_ == 'npadvmod':
                _append_token_before_adjs(t, 'time', token, adjs)
            else:
                _append_token_before_adjs(t, 'objects', token, adjs)
        elif token.pos_ == 'PRON':
            if token.dep_ == 'npadvmod':
                _append_token_before_adjs(t, 'time', token, adjs)
            elif not t['subjects']:
                # just append first subject
                _append_token_before_adjs(t, 'subjects', token, adjs)
        elif token.pos_ == 'ADJ':
            adjs.append(token.text)
    return t


@app.route("/", methods=["POST"])
def get_better_grammar():
    s = request.get_json()['data']
    return jsonify(get_tokens(nlp(s)))


if __name__ == "__main__":
    app.run()
