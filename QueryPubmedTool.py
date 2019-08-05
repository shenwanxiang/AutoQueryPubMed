from tqdm import tqdm
import pandas as pd
from pymed import PubMed
tqdm.pandas(ascii=True)
import fire, logging, time


def smart_strip(x):
    if x:
        return x.strip()
    else:
        return x


def hightlight_null(row):
    color = 'red' if row.isna().sum() >= 6 else 'white'
    return ['background-color: %s' % color for x in row]


def PubMedQuery(Inputfile, Outputfile, AdditionalKeyWords, verbose = False):
    '''
    parameters
    ---------------
    Inputfile: str, input file, like './input.txt';
    Outputfile: str, output file, like './test.xlsx'
    AdditionalKeyWords: str, keywords, like ' "pharmacy chemistry biology" '
    '''
    
    with open(Inputfile, 'r') as f:
        drugs = f.readlines()
    drugs = [i.strip() for i in drugs]

    pubmed = PubMed(tool="Query-Pubmed-Toolbox", email="wanxiang.shen@u.nus.edu")
    al = []
    with tqdm(total = len(drugs), ascii=True) as pbar:
        while drugs:
            time.sleep(0.5)
            drug  = drugs[0]
            try:
                if verbose:
                    pbar.write('Query: %s' % (drug + ' '+ smart_strip(AdditionalKeyWords)))
                results = pubmed.query(drug + ' '+ smart_strip(AdditionalKeyWords),  max_results=5)
                results = list(results)
                if results:
                    for res in results:
                            mydict = {'drug':drug,
                                    'pubmid':';'.join([smart_strip(i) for i in  res.pubmed_id.split('\n')]),
                                    'title':smart_strip(res.title),
                                    'journal': smart_strip(res.journal),
                                    'abstract':smart_strip(res.abstract),
                                    'doi':res.doi,
                                    'year': res.publication_date.year}

                            al.append(mydict)
                else: 
                    logging.warning('not found for %s' % drug + ' '+ AdditionalKeyWords)
                    al.append({'drug':drug})

                drugs.pop(0)
                pbar.update(1)
            except: pass
    df = pd.DataFrame(al)
    if '.xlsx' not in Outputfile:
        Outputfile = Outputfile + '.xlsx'
    sdf = df.style.apply(hightlight_null, axis=1)
    sdf.to_excel('Outputfile')
    sdf.to_pickle('.temp.pkl')
    
if __name__ == '__main__':
    fire.Fire(PubMedQuery)