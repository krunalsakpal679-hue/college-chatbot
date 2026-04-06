import requests, time
import codecs

with codecs.open('out.txt', 'w', 'utf-8') as f:
    U='http://127.0.0.1:8000/api/v1/chat/'
    tests=[
        ('EN1','What are the fees for B.Tech CSE?'),
        ('EN2','Tell me about placement'),
        ('HI1','B.Tech ki fees kitni hai?'),
        ('HI2','kese ho bhai?'),
        ('GU1','fees ketla che?'),
        ('GU2','placement pachhi salary ketla?'),
    ]
    for l,q in tests:
        r=requests.post(U,json={'query':q},timeout=30).json()
        lang = r['detected_language']
        resp = r['response'][:100].replace('\n',' ')
        f.write(f'{l} | LANG={lang} | {resp}\n')
        print(f'Finished {l}')
        time.sleep(3)
