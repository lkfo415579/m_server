import json, requests

class StanfordCoreNLP:

    def __init__(self, server_url):
        if server_url[-1] == '/':
            server_url = server_url[:-1]
        self.server_url = server_url

    def annotate(self, text, properties={
        'annotators': 'tokenize,ssplit,pos,lemma,ner',
        'outputFormat': 'json'
        }):
        # assert isinstance(text, str)
        if properties is None:
            properties = {}
        else:
            assert isinstance(properties, dict)

        # Checks that the Stanford CoreNLP server is started.
        try:
            requests.get(self.server_url)
        except requests.exceptions.ConnectionError:
            raise Exception('Check whether you have started the CoreNLP server e.g.\n'
            '$ cd stanford-corenlp-full-2015-12-09/ \n'
            '$ java -mx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer')

        data = text.encode('utf-8')
        #data = text.encode()
        r = requests.post(
            self.server_url, params={
                'properties': str(properties)
            }, data=data, headers={'Connection': 'close'})
        output = r.text
        if ('outputFormat' in properties
             and properties['outputFormat'] == 'json'):
            try:
                output = json.loads(output, encoding='utf-8', strict=True)
            except:
                pass
        return output

    def tokensregex(self, text, pattern, filter):
        return self.regex('/tokensregex', text, pattern, filter)

    def semgrex(self, text, pattern, filter):
        return self.regex('/semgrex', text, pattern, filter)

    def regex(self, endpoint, text, pattern, filter):
        r = requests.get(
            self.server_url + endpoint, params={
                'pattern':  pattern,
                'filter': filter
            }, data=text)
        output = r.text
        try:
            output = json.loads(r.text)
        except:
            pass
        return output
    def convert_NER(self,coreNLP_output):
        sentence = ""
        for sent in coreNLP_output['sentences']:
            for index,token in enumerate(sent['tokens']):
                if 'normalizedNER' in token and token['ner'] != 'ORDINAL':
                    #got a !
                    now_NER = token['normalizedNER']
                    #print "DEBUG:NER:",now_NER
                    list_del = []
                    for x in range(index+1,len(sent['tokens'])):
                        if 'normalizedNER' in sent['tokens'][x]:
                            if now_NER == sent['tokens'][x]['normalizedNER']:
                                #same
                                list_del.append(x)
                        else:
                            break
                    for index,ele in enumerate(list_del):
                        del sent['tokens'][ele-index]

                    #finished processing
                    if 'before' in token:
                        sentence += token['before'] + token['normalizedNER']
                    else:
                        sentence += token['normalizedNER']
                else:
                    if token['originalText'] == "":
                        word = token['word']
                    else:
                        word = token['originalText']
                    if 'before' in token:
                        sentence += token['before'] + word
                    else:
                        sentence += word
            #sentence += " "
        #print "sentence:",sentence
        return sentence
