your_tool_name = "SomeTool"
your_email = "SomeEmail@mail.ru"
nArticlesInHtml = 5000 #How many articles to write in html

good_keywords = {'glucosepane': 2.0, 'advanced glycation': 1.0, 'crosslink': 1.0, 'matrix': 0.8, 'extracellular matrix': 0.6,
'metalloproteinase': 0.9, 'nuclear pore complex': 0.8, 'stiff': 0.4, 'ecm': 1.0, 'elastin': 0.8,
'crispr': 2.0,  're:gene therapy|genetic therapy': 1.0,
're:tissue engineering|tissue-engineer': 1.0, 'bioprinting': 1.0, 'cell sheet': 0.5, 'regeneration': 0.4, 'stem cell': 0.2, 'xenotransplant': 0.8,
'deep learning': 1.2, 'artificial': 0.4, 'machine learning': 0.4,
'mediterranean':1.0, 'diet':0.2, 'ahei':1.0, 'eating index': 0.5, 'pulse wave': 0.8, 'vo2': 1.0, 'physical  activity':0.5, 'lifestyle':0.8, 'healthy factor': 0.5, 'healthy behav': 0.5, 'longevity': 1.4, 'life expectancy': 1.4, 'immortality': 2.0, 
'methylation clock': 0.4, 'senescent cell': 1.0, 'senescence': 0.3, 
'centenarian': 2.0, 'nonagenarian': 1.5, 'octagenarian': 1.5, 'ageing': 1.0, 'age-related': 1.0, 'with age': 0.5, 're:(?<=[^a-zA-Z])aging': 1.0, 
'nhanes': 0.2, 'uk biobank': 0.2,   're:russia|soviet': 1.0, 'kaplan': 0.5, 'anencephal': 1.0,     'alzheimer': 0.4, 'dementia': 0.3, 'connectom': 0.3,   'cryopreservation': 0.3,  're:all-cause|all cause': 3.5, 'income': 0.2, 'married': 0.2, 'marital': 0.2, } #
#(?=[^a-zA-Z])
bad_keywords = {'down syndrome': -3.0, 'surgery': -3.0, 'fracture': -1.5, 'asthma': -2.0, 'SARS-CoV': -2.0, 'Covid':-2.0, 'coronavirus':-2.0, 'retrospective': -0.3, 'heart failure': -3.0, 'acute': -3.0, 'injury': -1.5, 'chemotherapy': -3.0}

bad_title_keywords = {'infarction': -3.0, 'coronary': -3.0, 'cancer': -2.0, 'patient': -1.0}

good_authors = {'Moskalev': 10.0, 'Leonid A Gavrilov': 10.0, 'Natalia S Gavrilova': 10.0, 'Tatsuya Shimizu': 10.0, 'Teruo Okano': 10.0, 'de Grey': 10.0, 'Nir Barzilai': 10.0, 'Shmookler': 10.0, 'Judith Campisi': 10.0, 'Alex Zhavoronkov': 10.0}

good_journals = {'Frontier':2, 'gerontology':2}
good_journals_strict = {'Science':2, 'Nature':2, 'Cell':2}
bad_journals = {'Hemodialysis':-5, 'obesity':-3, 'surgery':-3, 'psychosocial oncology':-3, 'Jornal':-2}

good_keywords_max = {'meta-analysis': 1.0, 'randomized controlled': 1.0, 'systematic review': 0.5, 'cochrane': 1.0, 'prospective': 0.3}

good_keywords_thresh = {'mortality': [2.0, 3], 'collagen': [0.6, 2]}


#### You don't need to modify anything below unless you want to. =)
good_keywords_re = {k[3:]:v for k,v in good_keywords.items() if k[:3] == "re:"}
good_keywords = {k:v for k,v in good_keywords.items() if k[:3] != "re:"}
bad_keywords, bad_title_keywords, good_keywords, good_keywords_max, good_keywords_thresh, good_authors, good_journals, good_journals_strict, bad_journals  = [{k.lower() : v for k,v in dictionary.items()} for dictionary in [bad_keywords, bad_title_keywords, good_keywords, good_keywords_max, good_keywords_thresh, good_authors, good_journals, good_journals_strict, bad_journals]] #just converting all keys of all keywords to lowercase
 
#TODO: Speed optimization.
#TODO: Memory optimization. All data spend ~100Gb.  Perhaps, some precalculation of ~10%percentile articles, save them, delete others
#TODO: Don't save current day (and may be previous 2) for they aren't full yet.   
#      Can be realized by saving label with each file. Which shows when it was downloaded. 
# python3.6 -m pip install pymed
from pymed import PubMed
import re
import numpy as np
import sys
import os
import _pickle as cPickle
import time
from datetime import datetime, date, timedelta
pubmed = PubMed(tool = your_tool_name, email = your_email)
delete_xml = True
print(sys.argv)
today = datetime.date(datetime.now())

if len(sys.argv) == 3:
    date1 = datetime.strptime(sys.argv[1], '%Y-%m-%d').date()
    date2 = datetime.strptime(sys.argv[2], '%Y-%m-%d').date()
elif len(sys.argv) == 2:
    date1 = datetime.strptime(sys.argv[1], '%Y-%m-%d').date()
    date2 = datetime.strptime(sys.argv[1], '%Y-%m-%d').date()
else:
    date1 = datetime.date(datetime.now()) - timedelta(1)
    date2 = datetime.date(datetime.now())

def my_mkdir(path):
    if not os.path.exists(path):
        os.makedirs(path)

my_mkdir('data')

colorMagenta = '#be00be'
colorGreen = '#00be00'
colorBlue = '#00bea0'

def insert_font_tags(t, arr):
    #arr is smth like [[iArr1, fc1], [iArr2, fc2], ...]  where fc - font_color; iArr - smth like [[9,1], [14,2], [29,1], [33,2], ...]
    #here we first merge all iArrs to [[9,1,fc1], [14,2,fc1], ... , [5,1,fc2], [8,2,fc2], ...]
    iArr = []
    for i in range(len(arr)):
        iArr_i = arr[i][0]; fc = arr[i][1];
        for j in range(len(iArr_i)):
            iArr.append([iArr_i[j][0], iArr_i[j][1], fc])
    t_ans = ''
    idx = 0
    for i, label, font_color in sorted(iArr, key=lambda x: x[0]):
        t_ans += t[idx:i]
        if label == 1:
            t_ans += '<font color="' + font_color + '">'
        else:
            t_ans += '</font>'
        idx = i
    t_ans += t[idx:]
    return t_ans

def process(t, d, final=True): #(text, dictionary, colorFunc):
    if_good = sum([d[keyword] for keyword in d.keys() if keyword in t])
    if not final:
        return [], if_good
    else:
        iArr = []
        for keyword in d.keys():
            if keyword in t:
                i1 = t.find(keyword)
                i2 = i1 + len(keyword)
                iArr.append([i1, 1]); iArr.append([i2, 2]);
        #t_ans = insert_font_tags(t, iArr, font_color)
        return iArr, if_good

def process_re(t, d, final=True): #(text, dictionary, colorFunc):
    if not final:
        return [], 0
    else:
        if_good = 0
        iArr = []
        for keyword in d.keys():
            curr = re.search(keyword, t) #[(m.start(0), m.end(0)) for m in re.finditer(keyword, t)] #t.lower().find(keyword.lower())
            if curr != None:
                i1 = curr.span()[0]; i2 = curr.span()[1];
                iArr.append([i1, 1]); iArr.append([i2, 2]);
                if_good += d[keyword]
        return iArr, if_good

def process_mult(t, d, final=True):
    if_good = max([d[keyword] for keyword in d.keys() if keyword in t] + [0])
    if not final:
        return [], if_good
    else:
        iArr = []
        for keyword in d.keys():
            if keyword in t:
                i1 = t.find(keyword)
                i2 = i1 + len(keyword)
                iArr.append([i1, 1]); iArr.append([i2, 2]);
        #t_ans = insert_font_tags(t, iArr, font_color)
        return iArr, if_good

def process_strict(t, d, final=True):
    if_good = sum([d[keyword] for keyword in d.keys() if keyword == t])
    if not final:
        return [], if_good
    else:
        iArr = []
        for keyword in d.keys():
            if keyword == t:
                i1 = t.find(keyword)
                i2 = i1 + len(keyword)
                iArr.append([i1, 1]); iArr.append([i2, 2]);
        #t_ans = insert_font_tags(t, iArr, font_color)
        return iArr, if_good

def process_thresh(t, d, font_color, final=True):
    if_good = sum([d[keyword][0] for keyword in d.keys() if    len(re.findall(keyword, t)) >= d[keyword][1]   ])
    if not final:
        return [], if_good
    else:
        iArr = []
        for keyword in d.keys():
            if keyword in t:
                if len(re.findall(keyword, t)) >= d[keyword][1]:
                    i1 = t.find(keyword); i2 = i1 + len(keyword);
                    iArr.append([i1, 1]); iArr.append([i2, 2]);
    return iArr, if_good

def add_article(articles, article, curr, results_i=None, final=True):
    #'pubmed_id', 'title', 'abstract', 'keywords', 'journal', 'publication_date', 'authors', 'methods', 'conclusions', 'results', 'copyrights', 'doi', 'xml'
    identifier = article.pubmed_id
    
    articles[identifier] = {}
    articles[identifier]['date'] = curr
    articles[identifier]['results_i'] = results_i
    abstract = article.abstract if 'abstract' in article.__slots__ and article.abstract else ''
    title = article.title if 'title' in article.__slots__ and article.title else ''
    journal = article.journal if 'journal' in article.__slots__ and article.journal else ''
    abstract_lower = abstract.lower(); title_lower = title.lower(); journal_lower = journal.lower(); #precalculate for speed
    if_good = - 0.0001 * len(abstract)
    if_good += -5/(365*10) * (today - articles[identifier]['date']).days # -5 points for every 10 years
    
    iArr1, if_good1 = process(abstract_lower, bad_keywords, final)
    iArr2, if_good2 = process(abstract_lower, good_keywords, final)
    iArr2re, if_good2re = process_re(abstract_lower, good_keywords_re, final)
    iArr2m, if_good2m = process_mult(abstract_lower, good_keywords_max, final)
    iArr3, if_good3 = process_thresh(abstract_lower, good_keywords_thresh, final)
    if_good += if_good1 + if_good2 + if_good2re + if_good2m + if_good3
    if final:
        articles[identifier]['abstract'] = insert_font_tags(abstract, [[iArr1, colorMagenta], [iArr2, colorGreen], [iArr2re, colorGreen], [iArr2m, colorGreen], [iArr3, colorBlue]])
    
    iArr1, if_good1 = process(title_lower, bad_keywords, final)
    iArr1t, if_good1t = process(title_lower, bad_title_keywords, final)
    iArr2, if_good2 = process(title_lower, good_keywords, final)
    iArr2re, if_good2re = process_re(title_lower, good_keywords_re, final)
    iArr2m, if_good2m = process_mult(title_lower, good_keywords_max, final)
    if_good += if_good1 + if_good1t + if_good2 + if_good2re + if_good2m
    if final:
        articles[identifier]['title'] = insert_font_tags(title, [[iArr1, colorMagenta], [iArr1t, colorMagenta], [iArr2, colorGreen], [iArr2re, colorGreen], [iArr2m, colorGreen]])
    
    iArr1, if_good1 = process(journal_lower, bad_journals, final)
    iArr2, if_good2 = process(journal_lower, good_journals, final)
    iArr3, if_good3 = process_strict(journal_lower, good_journals_strict, final)
    if_good += if_good1 + if_good2 + if_good3
    if final:
        articles[identifier]['journal'] = insert_font_tags(journal, [[iArr1, colorMagenta], [iArr2, colorGreen], [iArr3, colorGreen]])
    
    creators = ', '.join([str(x['firstname']) + ' ' + str(x['lastname']) for x in article.authors])
    iArr1, if_good1 = process(creators.lower(), good_authors, final)
    if_good += if_good1
    if final:
        articles[identifier]['creators'] = insert_font_tags(creators, [[iArr1, '#00a000']])
    #creators = creators.lower()
    #for good_author in good_authors:
    #    if creators.find(good_author) > -1:
    #        # gives false positives on many "...ng A..."  like "Cheung Ang"
    #        red_idx = creators.find(good_author)
    #        creators = creators[:red_idx] + '<font color="#00a000"><b>' + creators[red_idx: red_idx + len(good_author)] \
    #        + '</b></font>' + creators[red_idx + len(good_author) :]
    #        articles[identifier]['if-good'] += 10
    #articles[identifier]['creators'] = creators
    articles[identifier]['if-good'] = if_good
    return articles

def save_pubmed_date_to_file(curr):
    my_mkdir(os.path.join('data/', str(curr.year)))
    query = '("' + curr.strftime("%Y/%m/%d") + '"[Date - Publication] : "' + curr.strftime("%Y/%m/%d") + '"[Date - Publication])'
    curr_results = pubmed.query(query, max_results=1000000)
    #curr_results = list(curr_results)
    counter = 0; nextpart_i = 0
    while True:
        curr_results_list = []
        counter_prev = counter
        for i in curr_results:
            curr_results_list.append(i)
            counter += 1
            if counter % 10000 == 0:
                print("counter = ", counter)
                curr_results_list.append('nextpart') #label that there would be next part
                break
        if counter_prev == counter:
            if counter % 10000 != 0 or counter == 0:
                break
            else:
                #the last 'nextpart' tag was a mistake. Let's remove it.
                with open('data/' + str(curr.year) + "/" + curr.strftime("%Y-%m-%d") + nextpartstr, 'rb') as f:
                    curr_results_list = cPickle.load(f)
                del curr_results_list[-1]
                with open('data/' + str(curr.year) + "/" + curr.strftime("%Y-%m-%d") + nextpartstr, 'wb') as f:
                    cPickle.dump(curr_results_list, f)
        if delete_xml:
            for i in range(min(10000, len(curr_results_list))):
                if 'xml' in curr_results_list[i].__slots__:
                    curr_results_list[i].xml = '' #decreases size 7x, and I don't use .xml here (yet? why it so large?)
        nextpart_i += 1
        nextpartstr = '' if nextpart_i <= 1 else 'part' + str(nextpart_i)
        with open('data/' + str(curr.year) + "/" + curr.strftime("%Y-%m-%d") + nextpartstr, 'wb') as f:
            cPickle.dump(curr_results_list, f)

results = {}
articles = {}
curr = date1
nextparti = 1
while curr <= date2:
    my_mkdir(os.path.join('data/', str(curr.year)))
    nextpartstr = '' if nextparti == 1 else 'part' + str(nextparti) #2021-01-01, 2021-01-01part2, 2021-01-01part3, etc
    if os.path.isfile('data/' + str(curr.year) + "/" + curr.strftime("%Y-%m-%d") + nextpartstr):
        with open('data/' + str(curr.year) + "/" + curr.strftime("%Y-%m-%d") + nextpartstr, 'rb') as f:
            curr_results_list = cPickle.load(f)
        if len(curr_results_list) == 0:
            curr += timedelta(1); print("File with zero articles! " + curr.strftime("%Y-%m-%d"))
            continue
        if curr_results_list[-1] == 'nextpart':
            nextparti += 1
            del curr_results_list[-1]
        else:
            nextparti = 1
    else:
        save_pubmed_date_to_file(curr)
        continue #curr has not been updated; so we try the same curr  and now we have it downloaded.
    
    time1 = time.time()
    curr_articles = {}
    for i in range(len(curr_results_list)):
        if '\n' in curr_results_list[i].pubmed_id: 
            #TODO: update all downloaded data to edit this.
            curr_results_list[i].pubmed_id = re.findall('.+(?=\n)', curr_results_list[i].pubmed_id)[0]
        
        curr_articles = add_article(curr_articles, curr_results_list[i], curr, i, final=False)
        if i % 100 == 0:
            print('\r' + str(np.ceil(i/len(curr_results_list)*100)) + '% progress' + ' '*5, end="")
    print('\r' + str(100) + '% progress' + ' '*5, end="")
    
    print(curr, nextpartstr, '-', len(curr_results_list), 'articles')
    print(time.time() - time1, 'seconds')
    articles = {**articles, **curr_articles}
    bestIDs = sorted(articles, key=lambda x: (articles[x]['if-good']), reverse=True)[:min(nArticlesInHtml,len(articles))]
    bestIDs = {x:0 for x in bestIDs}
    articles = {k:v for k,v in articles.items() if k in bestIDs}
    curr_results_list = {x.pubmed_id :x for x in curr_results_list if x.pubmed_id in articles.keys()}
    results = {**results, **curr_results_list}
    #print("1 = ", len(results))
    results = {k:v for k,v in results.items() if k in bestIDs}
    #print("2 = ", len(results))
    if nextparti == 1:
        curr = curr + timedelta(days=1)

#exit()


articles_final = {}
for currID in sorted(articles, key=lambda x: (articles[x]['if-good']), reverse=True)[:nArticlesInHtml]:
    articles_final = add_article(articles_final, results[currID], articles[currID]['date'], results_i=None, final=True)

print(time.time() - time1, 'seconds')

fW = open("pubmed-summary.html", "w+", encoding="utf-8")
if len(sys.argv) > 1:
    for i in range(1, len(sys.argv)):
        fW.write(sys.argv[i] + " ")
    fW.write("</br></br>\n")

nummer = 1
for currID in sorted(articles_final, key=lambda x: (articles_final[x]['if-good']), reverse=True):
    fW.write("<a href='https://pubmed.ncbi.nlm.nih.gov/" + currID + "'>" + currID + "</a> &nbsp&nbsp ")
    fW.write(articles_final[currID]['journal'])
    fW.write(" &nbsp&nbsp " + "{:.4f}".format(articles_final[currID]['if-good']) + " points, " + articles_final[currID]['date'].strftime("%Y/%m/%d") + ", #" + str(nummer) + "</br>\n")
    fW.write("<b>" + articles_final[currID]['title'] + "</b></br>\n")
    fW.write("Authors: " + articles_final[currID]['creators'] + "</br>\n")
    fW.write(articles_final[currID]['abstract'] + "</br></br>\n\n")
    nummer += 1
    if nummer > nArticlesInHtml:
        break

fW.close()
print('Ready! See file "pubmed-summary.html"')

